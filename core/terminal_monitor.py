import os
import subprocess
import threading
import time
import logging
import psutil
import re
from datetime import datetime, timedelta
from collections import deque
from typing import Dict, List, Optional, Tuple
import json
from pathlib import Path

logger = logging.getLogger(__name__)

class TerminalMonitor:
    """Comprehensive terminal activity monitoring system."""
    
    def __init__(self):
        self.is_monitoring = False
        self.monitor_thread = None
        self.terminal_buffer = deque(maxlen=1000)
        self.command_history = deque(maxlen=500)
        self.process_history = deque(maxlen=200)
        self.current_session_pid = os.getpid()
        self.parent_shell_pid = os.getppid()
        self.lock = threading.Lock()
        
        # Initialize monitoring components
        self.shell_history_monitor = ShellHistoryMonitor()
        self.process_monitor = ProcessMonitor()
        self.terminal_content_monitor = TerminalContentMonitor()
        
        logger.info("Terminal Monitor initialized")

    def start_monitoring(self):
        """Start comprehensive terminal monitoring."""
        if self.is_monitoring:
            return
            
        self.is_monitoring = True
        
        # Start all monitoring components
        self.shell_history_monitor.start()
        self.process_monitor.start()
        self.terminal_content_monitor.start()
        
        # Start main monitoring thread
        self.monitor_thread = threading.Thread(target=self._monitor_loop, daemon=True)
        self.monitor_thread.start()
        
        logger.info("Terminal monitoring started")

    def stop_monitoring(self):
        """Stop all monitoring."""
        self.is_monitoring = False
        
        # Stop all components
        self.shell_history_monitor.stop()
        self.process_monitor.stop()
        self.terminal_content_monitor.stop()
        
        if self.monitor_thread:
            self.monitor_thread.join(timeout=2)
            
        logger.info("Terminal monitoring stopped")

    def _monitor_loop(self):
        """Main monitoring loop that aggregates data from all sources."""
        while self.is_monitoring:
            try:
                # Collect data from all monitors
                with self.lock:
                    # Get shell history updates
                    new_commands = self.shell_history_monitor.get_new_commands()
                    for cmd in new_commands:
                        self.command_history.append(cmd)
                        self.terminal_buffer.append(f"[{cmd['timestamp']}] $ {cmd['command']}")
                    
                    # Get process updates
                    new_processes = self.process_monitor.get_new_processes()
                    for proc in new_processes:
                        self.process_history.append(proc)
                    
                    # Get terminal content updates
                    new_content = self.terminal_content_monitor.get_new_content()
                    for content in new_content:
                        self.terminal_buffer.append(content)
                
                time.sleep(1)  # Check every second
                
            except Exception as e:
                logger.error(f"Error in monitoring loop: {e}")
                time.sleep(5)

    def get_terminal_context(self, lines: int = 50, include_history: bool = True) -> str:
        """Get comprehensive terminal context."""
        with self.lock:
            context_parts = []
            
            # Current terminal state
            context_parts.append(f"Current Directory: {os.getcwd()}")
            context_parts.append(f"Terminal PID: {self.current_session_pid}")
            context_parts.append(f"Shell PID: {self.parent_shell_pid}")
            context_parts.append(f"User: {os.getenv('USER', 'unknown')}")
            context_parts.append("")
            
            # Recent terminal buffer
            if self.terminal_buffer:
                context_parts.append("=== Recent Terminal Activity ===")
                recent_buffer = list(self.terminal_buffer)[-lines:]
                context_parts.extend(recent_buffer)
                context_parts.append("")
            
            # Shell history if requested
            if include_history and self.command_history:
                context_parts.append("=== Command History ===")
                recent_commands = list(self.command_history)[-20:]
                for cmd in recent_commands:
                    context_parts.append(f"[{cmd['timestamp']}] {cmd['command']}")
                context_parts.append("")
            
            # Running processes
            context_parts.append("=== Active Processes ===")
            try:
                current_processes = []
                for proc in psutil.process_iter(['pid', 'name', 'cmdline']):
                    try:
                        if proc.info['pid'] != self.current_session_pid:
                            cmdline = ' '.join(proc.info['cmdline']) if proc.info['cmdline'] else proc.info['name']
                            if len(cmdline) > 100:
                                cmdline = cmdline[:100] + "..."
                            current_processes.append(f"PID {proc.info['pid']}: {cmdline}")
                    except (psutil.NoSuchProcess, psutil.AccessDenied):
                        continue
                
                # Show most recent processes
                for proc in current_processes[-10:]:
                    context_parts.append(proc)
                    
            except Exception as e:
                context_parts.append(f"Error getting processes: {e}")
            
            return "\n".join(context_parts)

    def get_full_session_history(self) -> Dict:
        """Get complete session history."""
        with self.lock:
            return {
                "session_start": datetime.now().isoformat(),
                "terminal_buffer": list(self.terminal_buffer),
                "command_history": list(self.command_history),
                "process_history": list(self.process_history),
                "current_directory": os.getcwd(),
                "environment": dict(os.environ)
            }


class ShellHistoryMonitor:
    """Monitor shell command history."""
    
    def __init__(self):
        self.is_running = False
        self.thread = None
        self.last_history_size = 0
        self.history_file = self._get_history_file()
        self.commands = deque(maxlen=100)
        
    def _get_history_file(self) -> Optional[str]:
        """Get the shell history file path."""
        shell = os.getenv('SHELL', '')
        home = os.path.expanduser('~')
        
        if 'bash' in shell:
            return os.path.join(home, '.bash_history')
        elif 'zsh' in shell:
            return os.path.join(home, '.zsh_history')
        elif 'fish' in shell:
            return os.path.join(home, '.local/share/fish/fish_history')
        else:
            # Try common locations
            for hist_file in ['.bash_history', '.zsh_history', '.history']:
                path = os.path.join(home, hist_file)
                if os.path.exists(path):
                    return path
        return None

    def start(self):
        """Start monitoring shell history."""
        if not self.history_file or not os.path.exists(self.history_file):
            logger.warning(f"Shell history file not found: {self.history_file}")
            return
            
        self.is_running = True
        self.thread = threading.Thread(target=self._monitor_history, daemon=True)
        self.thread.start()
        logger.info(f"Shell history monitoring started: {self.history_file}")

    def stop(self):
        """Stop monitoring."""
        self.is_running = False
        if self.thread:
            self.thread.join(timeout=2)

    def _monitor_history(self):
        """Monitor shell history file for changes."""
        while self.is_running:
            try:
                if os.path.exists(self.history_file):
                    stat = os.stat(self.history_file)
                    current_size = stat.st_size
                    
                    if current_size != self.last_history_size:
                        self._read_new_history()
                        self.last_history_size = current_size
                        
                time.sleep(2)
                
            except Exception as e:
                logger.error(f"Error monitoring history: {e}")
                time.sleep(5)

    def _read_new_history(self):
        """Read new commands from history file."""
        try:
            with open(self.history_file, 'r', encoding='utf-8', errors='ignore') as f:
                lines = f.readlines()
                
            # Get recent commands
            recent_lines = lines[-50:] if len(lines) > 50 else lines
            
            for line in recent_lines:
                line = line.strip()
                if line and not line.startswith('#'):
                    # Handle zsh history format (with timestamps)
                    if line.startswith(': '):
                        parts = line.split(';', 1)
                        if len(parts) > 1:
                            command = parts[1].strip()
                        else:
                            command = line
                    else:
                        command = line
                    
                    if command:
                        cmd_entry = {
                            "timestamp": datetime.now().strftime('%H:%M:%S'),
                            "command": command,
                            "source": "history"
                        }
                        
                        # Avoid duplicates
                        if not self.commands or self.commands[-1]["command"] != command:
                            self.commands.append(cmd_entry)
                            
        except Exception as e:
            logger.error(f"Error reading history file: {e}")

    def get_new_commands(self) -> List[Dict]:
        """Get new commands since last check."""
        commands = list(self.commands)
        self.commands.clear()
        return commands


class ProcessMonitor:
    """Monitor system processes for terminal-related activity."""
    
    def __init__(self):
        self.is_running = False
        self.thread = None
        self.processes = deque(maxlen=50)
        self.known_pids = set()

    def start(self):
        """Start process monitoring."""
        self.is_running = True
        self.thread = threading.Thread(target=self._monitor_processes, daemon=True)
        self.thread.start()
        logger.info("Process monitoring started")

    def stop(self):
        """Stop monitoring."""
        self.is_running = False
        if self.thread:
            self.thread.join(timeout=2)

    def _monitor_processes(self):
        """Monitor system processes."""
        while self.is_running:
            try:
                current_pids = set()
                for proc in psutil.process_iter(['pid', 'name', 'cmdline', 'create_time']):
                    try:
                        pid = proc.info['pid']
                        current_pids.add(pid)
                        
                        # Check for new processes
                        if pid not in self.known_pids:
                            cmdline = ' '.join(proc.info['cmdline']) if proc.info['cmdline'] else proc.info['name']
                            
                            # Filter for interesting processes (shells, editors, etc.)
                            if self._is_interesting_process(proc.info['name'], cmdline):
                                proc_entry = {
                                    "pid": pid,
                                    "name": proc.info['name'],
                                    "cmdline": cmdline,
                                    "timestamp": datetime.now().strftime('%H:%M:%S'),
                                    "action": "started"
                                }
                                self.processes.append(proc_entry)
                        
                    except (psutil.NoSuchProcess, psutil.AccessDenied):
                        continue
                
                # Check for terminated processes
                terminated_pids = self.known_pids - current_pids
                for pid in terminated_pids:
                    proc_entry = {
                        "pid": pid,
                        "timestamp": datetime.now().strftime('%H:%M:%S'),
                        "action": "terminated"
                    }
                    self.processes.append(proc_entry)
                
                self.known_pids = current_pids
                time.sleep(3)
                
            except Exception as e:
                logger.error(f"Error monitoring processes: {e}")
                time.sleep(5)

    def _is_interesting_process(self, name: str, cmdline: str) -> bool:
        """Check if process is interesting for terminal monitoring."""
        interesting_names = ['bash', 'zsh', 'fish', 'sh', 'python', 'node', 'vim', 'nano', 'emacs', 'git', 'docker', 'kubectl']
        interesting_patterns = ['ssh', 'rsync', 'curl', 'wget', 'pip', 'npm', 'yarn']
        
        name_lower = name.lower()
        cmdline_lower = cmdline.lower()
        
        # Check process name
        if any(interesting in name_lower for interesting in interesting_names):
            return True
            
        # Check command line
        if any(pattern in cmdline_lower for pattern in interesting_patterns):
            return True
            
        return False

    def get_new_processes(self) -> List[Dict]:
        """Get new process events."""
        processes = list(self.processes)
        self.processes.clear()
        return processes


class TerminalContentMonitor:
    """Monitor terminal content and output."""
    
    def __init__(self):
        self.is_running = False
        self.thread = None
        self.content = deque(maxlen=100)
        
    def start(self):
        """Start terminal content monitoring."""
        self.is_running = True
        self.thread = threading.Thread(target=self._monitor_content, daemon=True)
        self.thread.start()
        logger.info("Terminal content monitoring started")

    def stop(self):
        """Stop monitoring."""
        self.is_running = False
        if self.thread:
            self.thread.join(timeout=2)

    def _monitor_content(self):
        """Monitor terminal content (basic implementation)."""
        while self.is_running:
            try:
                # This is a simplified approach - in practice, you might want to use
                # more sophisticated methods like screen scraping or terminal hooks
                
                # Monitor for interesting system changes
                self._check_directory_changes()
                self._check_environment_changes()
                
                time.sleep(5)
                
            except Exception as e:
                logger.error(f"Error monitoring terminal content: {e}")
                time.sleep(10)

    def _check_directory_changes(self):
        """Check for directory changes."""
        # This is a basic implementation - could be enhanced
        pass

    def _check_environment_changes(self):
        """Check for environment variable changes."""
        # This is a basic implementation - could be enhanced
        pass

    def get_new_content(self) -> List[str]:
        """Get new terminal content."""
        content = list(self.content)
        self.content.clear()
        return content


# Enhanced integration functions
def setup_shell_integration():
    """Setup shell integration for comprehensive monitoring."""
    shell = os.getenv('SHELL', '')
    home = os.path.expanduser('~')
    
    # Create shell integration script
    integration_script = '''
# SheLLM Terminal Integration
export SHELLM_PID=$$
export SHELLM_SESSION_ID=$(date +%s)

# Function to log commands to SheLLM server
shellm_log_command() {
    if [ -n "$1" ]; then
        curl -s -X POST http://localhost:8000/log/command \
            --data-urlencode "command=$1" \
            --connect-timeout 1 > /dev/null 2>&1 || true
    fi
}

# Function to log command output
shellm_log_output() {
    if [ -n "$1" ] && [ -n "$2" ]; then
        curl -s -X POST http://localhost:8000/log/output \
            --data-urlencode "command=$1" \
            --data-urlencode "output=$2" \
            --connect-timeout 1 > /dev/null 2>&1 || true
    fi
}

# Hook into command execution (bash)
if [ -n "$BASH_VERSION" ]; then
    trap 'shellm_log_command "$(history 1 | sed "s/^[ ]*[0-9]*[ ]*//")"' DEBUG
fi

# Hook into command execution (zsh)
if [ -n "$ZSH_VERSION" ]; then
    preexec() {
        shellm_log_command "$1"
    }
fi
'''
    
    integration_file = os.path.join(home, '.shellm_integration')
    try:
        with open(integration_file, 'w') as f:
            f.write(integration_script)
        
        logger.info(f"Shell integration script created: {integration_file}")
        logger.info("Add 'source ~/.shellm_integration' to your shell rc file")
        return integration_file
        
    except Exception as e:
        logger.error(f"Error creating shell integration: {e}")
        return None


def get_terminal_scrollback() -> str:
    """Attempt to get terminal scrollback buffer."""
    try:
        # Try to get terminal content using various methods
        methods = [
            _get_scrollback_screen,
            _get_scrollback_tmux,
            _get_scrollback_history
        ]
        
        for method in methods:
            try:
                result = method()
                if result:
                    return result
            except Exception as e:
                logger.debug(f"Method failed: {e}")
                continue
        
        return "Unable to retrieve terminal scrollback"
        
    except Exception as e:
        logger.error(f"Error getting terminal scrollback: {e}")
        return f"Error: {e}"


def _get_scrollback_screen() -> Optional[str]:
    """Get scrollback from screen session."""
    try:
        result = subprocess.run(['screen', '-ls'], capture_output=True, text=True)
        if result.returncode == 0 and 'Sockets' in result.stdout:
            # We're in a screen session
            return "Screen session detected - scrollback monitoring available"
    except FileNotFoundError:
        pass
    return None


def _get_scrollback_tmux() -> Optional[str]:
    """Get scrollback from tmux session."""
    try:
        result = subprocess.run(['tmux', 'capture-pane', '-p'], capture_output=True, text=True)
        if result.returncode == 0:
            return f"Tmux session content:\n{result.stdout}"
    except FileNotFoundError:
        pass
    return None


def _get_scrollback_history() -> Optional[str]:
    """Get content from shell history."""
    try:
        result = subprocess.run(['history', '50'], capture_output=True, text=True, shell=True)
        if result.returncode == 0:
            return f"Shell history:\n{result.stdout}"
    except Exception:
        pass
    return None 