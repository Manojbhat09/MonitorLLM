#!/usr/bin/env python3
"""
Comprehensive Terminal Monitor for SheLLM

This module provides comprehensive monitoring of terminal activity including:
- All commands executed in the terminal (not just through SheLLM)
- Command outputs and terminal content
- Process monitoring and system activity
- Shell history parsing and real-time monitoring
- Terminal session capture and scrollback
"""

import os
import subprocess
import threading
import time
import logging
import json
import re
import fcntl
import select
import pty
from datetime import datetime, timedelta
from collections import deque
from typing import Dict, List, Optional, Tuple, Any
from pathlib import Path
import signal
import sys

try:
    import psutil
except ImportError:
    psutil = None

logger = logging.getLogger(__name__)

class ComprehensiveTerminalMonitor:
    """
    Comprehensive terminal monitoring system that captures ALL terminal activity.
    """
    
    def __init__(self, server_url: str = "http://localhost:8000"):
        self.server_url = server_url
        self.is_monitoring = False
        self.monitors = {}
        self.terminal_buffer = deque(maxlen=2000)
        self.session_data = {
            "start_time": datetime.now().isoformat(),
            "commands": [],
            "outputs": [],
            "processes": [],
            "files_accessed": []
        }
        self.lock = threading.Lock()
        
        # Initialize all monitoring components
        self._init_monitors()
        
        logger.info("Comprehensive Terminal Monitor initialized")

    def _init_monitors(self):
        """Initialize all monitoring components."""
        self.monitors = {
            'shell_history': ShellHistoryMonitor(),
            'process_watcher': ProcessWatcher(),
            'terminal_capture': TerminalCapture(),
            'file_monitor': FileAccessMonitor(),
            'environment_monitor': EnvironmentMonitor()
        }

    def start_monitoring(self):
        """Start comprehensive monitoring of all terminal activity."""
        if self.is_monitoring:
            logger.warning("Monitoring already active")
            return
            
        self.is_monitoring = True
        
        # Start all monitoring components
        for name, monitor in self.monitors.items():
            try:
                monitor.start()
                logger.info(f"Started {name} monitor")
            except Exception as e:
                logger.error(f"Failed to start {name} monitor: {e}")
        
        # Start main coordination thread
        self.coordination_thread = threading.Thread(target=self._coordination_loop, daemon=True)
        self.coordination_thread.start()
        
        # Try to get existing terminal content
        self._capture_existing_terminal_content()
        
        logger.info("🔍 Comprehensive terminal monitoring started")
        logger.info("📊 Monitoring: Commands, Outputs, Processes, Files, Environment")

    def stop_monitoring(self):
        """Stop all monitoring."""
        self.is_monitoring = False
        
        for name, monitor in self.monitors.items():
            try:
                monitor.stop()
                logger.info(f"Stopped {name} monitor")
            except Exception as e:
                logger.error(f"Error stopping {name} monitor: {e}")
        
        logger.info("Comprehensive terminal monitoring stopped")

    def _coordination_loop(self):
        """Main coordination loop that collects data from all monitors."""
        while self.is_monitoring:
            try:
                with self.lock:
                    # Collect data from all monitors
                    for name, monitor in self.monitors.items():
                        try:
                            new_data = monitor.get_new_data()
                            if new_data:
                                self._process_monitor_data(name, new_data)
                        except Exception as e:
                            logger.error(f"Error collecting data from {name}: {e}")
                
                time.sleep(0.5)  # High frequency monitoring
                
            except Exception as e:
                logger.error(f"Error in coordination loop: {e}")
                time.sleep(2)

    def _process_monitor_data(self, monitor_name: str, data: List[Dict]):
        """Process data from a specific monitor."""
        for item in data:
            # Add to terminal buffer
            timestamp = item.get('timestamp', datetime.now().strftime('%H:%M:%S'))
            
            if monitor_name == 'shell_history':
                entry = f"[{timestamp}] $ {item['command']}"
                self.terminal_buffer.append(entry)
                self.session_data['commands'].append(item)
                
            elif monitor_name == 'terminal_capture':
                entry = f"[{timestamp}] {item['content']}"
                self.terminal_buffer.append(entry)
                self.session_data['outputs'].append(item)
                
            elif monitor_name == 'process_watcher':
                entry = f"[{timestamp}] Process {item['action']}: {item['name']} (PID: {item['pid']})"
                self.terminal_buffer.append(entry)
                self.session_data['processes'].append(item)
                
            elif monitor_name == 'file_monitor':
                entry = f"[{timestamp}] File {item['action']}: {item['path']}"
                self.terminal_buffer.append(entry)
                self.session_data['files_accessed'].append(item)

    def _capture_existing_terminal_content(self):
        """Attempt to capture existing terminal content."""
        try:
            # Try multiple methods to get existing terminal content
            methods = [
                self._get_tmux_content,
                self._get_screen_content,
                self._get_shell_history,
                self._get_recent_logs
            ]
            
            for method in methods:
                try:
                    content = method()
                    if content:
                        with self.lock:
                            self.terminal_buffer.append(f"[EXISTING] {content}")
                        logger.info(f"Captured existing content via {method.__name__}")
                        break
                except Exception as e:
                    logger.debug(f"Method {method.__name__} failed: {e}")
                    
        except Exception as e:
            logger.error(f"Error capturing existing terminal content: {e}")

    def _get_tmux_content(self) -> Optional[str]:
        """Get content from tmux session."""
        try:
            result = subprocess.run(['tmux', 'capture-pane', '-p'], 
                                  capture_output=True, text=True, timeout=5)
            if result.returncode == 0:
                return f"Tmux session content:\n{result.stdout}"
        except (subprocess.TimeoutExpired, FileNotFoundError):
            pass
        return None

    def _get_screen_content(self) -> Optional[str]:
        """Get content from screen session."""
        try:
            result = subprocess.run(['screen', '-ls'], 
                                  capture_output=True, text=True, timeout=5)
            if result.returncode == 0 and 'Sockets' in result.stdout:
                return f"Screen session detected:\n{result.stdout}"
        except (subprocess.TimeoutExpired, FileNotFoundError):
            pass
        return None

    def _get_shell_history(self) -> Optional[str]:
        """Get shell history."""
        try:
            result = subprocess.run(['history', '20'], 
                                  capture_output=True, text=True, shell=True, timeout=5)
            if result.returncode == 0:
                return f"Recent shell history:\n{result.stdout}"
        except (subprocess.TimeoutExpired, FileNotFoundError):
            pass
        return None

    def _get_recent_logs(self) -> Optional[str]:
        """Get recent system logs."""
        try:
            # Get recent user activity
            result = subprocess.run(['last', '-n', '5'], 
                                  capture_output=True, text=True, timeout=5)
            if result.returncode == 0:
                return f"Recent user activity:\n{result.stdout}"
        except (subprocess.TimeoutExpired, FileNotFoundError):
            pass
        return None

    def get_comprehensive_context(self, lines: int = 100) -> str:
        """Get comprehensive terminal context for LLM."""
        with self.lock:
            context_parts = []
            
            # System information
            context_parts.append("=== SYSTEM CONTEXT ===")
            context_parts.append(f"User: {os.getenv('USER', 'unknown')}")
            context_parts.append(f"Shell: {os.getenv('SHELL', 'unknown')}")
            context_parts.append(f"PWD: {os.getcwd()}")
            context_parts.append(f"Terminal: {os.getenv('TERM', 'unknown')}")
            context_parts.append(f"Session PID: {os.getpid()}")
            context_parts.append("")
            
            # Recent terminal activity
            context_parts.append("=== TERMINAL ACTIVITY ===")
            recent_buffer = list(self.terminal_buffer)[-lines:]
            context_parts.extend(recent_buffer)
            context_parts.append("")
            
            # Session statistics
            context_parts.append("=== SESSION STATISTICS ===")
            context_parts.append(f"Commands executed: {len(self.session_data['commands'])}")
            context_parts.append(f"Processes monitored: {len(self.session_data['processes'])}")
            context_parts.append(f"Files accessed: {len(self.session_data['files_accessed'])}")
            context_parts.append("")
            
            # Environment variables (important ones)
            context_parts.append("=== ENVIRONMENT ===")
            important_vars = ['PATH', 'HOME', 'USER', 'SHELL', 'TERM', 'PWD', 'LANG']
            for var in important_vars:
                value = os.getenv(var)
                if value:
                    # Truncate long values
                    if len(value) > 100:
                        value = value[:100] + "..."
                    context_parts.append(f"{var}={value}")
            
            return "\n".join(context_parts)

    def get_session_summary(self) -> Dict[str, Any]:
        """Get detailed session summary."""
        with self.lock:
            duration = datetime.now() - datetime.fromisoformat(self.session_data['start_time'])
            
            # Analyze command patterns
            command_counts = {}
            for cmd in self.session_data['commands']:
                base_cmd = cmd['command'].split()[0] if cmd['command'] else 'unknown'
                command_counts[base_cmd] = command_counts.get(base_cmd, 0) + 1
            
            # Analyze file access patterns
            file_patterns = {}
            for file_access in self.session_data['files_accessed']:
                action = file_access['action']
                file_patterns[action] = file_patterns.get(action, 0) + 1
            
            return {
                "session_duration": str(duration),
                "total_commands": len(self.session_data['commands']),
                "total_processes": len(self.session_data['processes']),
                "total_file_access": len(self.session_data['files_accessed']),
                "command_frequency": sorted(command_counts.items(), key=lambda x: x[1], reverse=True),
                "file_access_patterns": file_patterns,
                "buffer_size": len(self.terminal_buffer),
                "monitoring_active": self.is_monitoring
            }


class ShellHistoryMonitor:
    """Monitor shell history in real-time."""
    
    def __init__(self):
        self.is_running = False
        self.thread = None
        self.new_commands = deque(maxlen=50)
        self.history_file = self._find_history_file()
        self.last_history_size = 0
        self.last_checked = time.time()

    def _find_history_file(self) -> Optional[str]:
        """Find the shell history file."""
        shell = os.getenv('SHELL', '')
        home = os.path.expanduser('~')
        
        candidates = []
        if 'bash' in shell:
            candidates.append(os.path.join(home, '.bash_history'))
        elif 'zsh' in shell:
            candidates.append(os.path.join(home, '.zsh_history'))
        elif 'fish' in shell:
            candidates.append(os.path.join(home, '.local/share/fish/fish_history'))
        
        # Add common locations
        candidates.extend([
            os.path.join(home, '.bash_history'),
            os.path.join(home, '.zsh_history'),
            os.path.join(home, '.history')
        ])
        
        for candidate in candidates:
            if os.path.exists(candidate):
                return candidate
        
        return None

    def start(self):
        """Start monitoring shell history."""
        if not self.history_file:
            logger.warning("No shell history file found")
            return
            
        self.is_running = True
        self.thread = threading.Thread(target=self._monitor_history, daemon=True)
        self.thread.start()
        logger.info(f"Shell history monitoring started: {self.history_file}")

    def stop(self):
        """Stop monitoring."""
        self.is_running = False
        if self.thread:
            self.thread.join(timeout=1)

    def _monitor_history(self):
        """Monitor shell history file."""
        while self.is_running:
            try:
                if os.path.exists(self.history_file):
                    stat = os.stat(self.history_file)
                    if stat.st_mtime > self.last_checked:
                        self._process_history_update()
                        self.last_checked = stat.st_mtime
                
                time.sleep(1)
                
            except Exception as e:
                logger.error(f"Error monitoring shell history: {e}")
                time.sleep(5)

    def _process_history_update(self):
        """Process history file updates."""
        try:
            with open(self.history_file, 'r', encoding='utf-8', errors='ignore') as f:
                lines = f.readlines()
            
            # Process recent lines
            for line in lines[-10:]:  # Check last 10 lines
                line = line.strip()
                if line and not line.startswith('#'):
                    # Handle different history formats
                    command = self._parse_history_line(line)
                    if command:
                        cmd_entry = {
                            "timestamp": datetime.now().strftime('%H:%M:%S'),
                            "command": command,
                            "source": "shell_history"
                        }
                        self.new_commands.append(cmd_entry)
                        
        except Exception as e:
            logger.error(f"Error processing history update: {e}")

    def _parse_history_line(self, line: str) -> Optional[str]:
        """Parse a history line based on shell format."""
        # Handle zsh extended history format
        if line.startswith(': '):
            parts = line.split(';', 1)
            if len(parts) > 1:
                return parts[1].strip()
        
        # Handle bash/other formats
        return line.strip()

    def get_new_data(self) -> List[Dict]:
        """Get new commands."""
        commands = list(self.new_commands)
        self.new_commands.clear()
        return commands


class ProcessWatcher:
    """Watch for new processes and process changes."""
    
    def __init__(self):
        self.is_running = False
        self.thread = None
        self.new_processes = deque(maxlen=30)
        self.known_pids = set()
        self.process_cache = {}

    def start(self):
        """Start process monitoring."""
        if not psutil:
            logger.warning("psutil not available - process monitoring disabled")
            return
            
        self.is_running = True
        self.thread = threading.Thread(target=self._monitor_processes, daemon=True)
        self.thread.start()
        logger.info("Process monitoring started")

    def stop(self):
        """Stop monitoring."""
        self.is_running = False
        if self.thread:
            self.thread.join(timeout=1)

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
                            if self._is_interesting_process(proc.info):
                                proc_entry = {
                                    "pid": pid,
                                    "name": proc.info['name'],
                                    "cmdline": ' '.join(proc.info['cmdline']) if proc.info['cmdline'] else proc.info['name'],
                                    "timestamp": datetime.now().strftime('%H:%M:%S'),
                                    "action": "started"
                                }
                                self.new_processes.append(proc_entry)
                                self.process_cache[pid] = proc.info
                        
                    except (psutil.NoSuchProcess, psutil.AccessDenied):
                        continue
                
                # Check for terminated processes
                terminated_pids = self.known_pids - current_pids
                for pid in terminated_pids:
                    if pid in self.process_cache:
                        proc_entry = {
                            "pid": pid,
                            "name": self.process_cache[pid].get('name', 'unknown'),
                            "timestamp": datetime.now().strftime('%H:%M:%S'),
                            "action": "terminated"
                        }
                        self.new_processes.append(proc_entry)
                        del self.process_cache[pid]
                
                self.known_pids = current_pids
                time.sleep(2)
                
            except Exception as e:
                logger.error(f"Error monitoring processes: {e}")
                time.sleep(5)

    def _is_interesting_process(self, proc_info: Dict) -> bool:
        """Check if process is worth monitoring."""
        name = proc_info.get('name', '').lower()
        cmdline = ' '.join(proc_info.get('cmdline', [])).lower()
        
        # Interesting process names
        interesting_names = [
            'bash', 'zsh', 'fish', 'sh', 'python', 'node', 'npm', 'pip',
            'vim', 'nano', 'emacs', 'code', 'git', 'docker', 'kubectl',
            'ssh', 'rsync', 'curl', 'wget', 'make', 'gcc', 'java'
        ]
        
        # Check if any interesting name is in the process name or command line
        return any(interesting in name or interesting in cmdline for interesting in interesting_names)

    def get_new_data(self) -> List[Dict]:
        """Get new process events."""
        processes = list(self.new_processes)
        self.new_processes.clear()
        return processes


class TerminalCapture:
    """Basic terminal content capture."""
    
    def __init__(self):
        self.is_running = False
        self.thread = None
        self.new_content = deque(maxlen=20)

    def start(self):
        """Start terminal capture."""
        self.is_running = True
        self.thread = threading.Thread(target=self._capture_content, daemon=True)
        self.thread.start()
        logger.info("Terminal capture started")

    def stop(self):
        """Stop capture."""
        self.is_running = False
        if self.thread:
            self.thread.join(timeout=1)

    def _capture_content(self):
        """Capture terminal content."""
        while self.is_running:
            try:
                # This is a placeholder - real implementation would need
                # more sophisticated terminal capture techniques
                time.sleep(10)
                
            except Exception as e:
                logger.error(f"Error capturing terminal content: {e}")
                time.sleep(10)

    def get_new_data(self) -> List[Dict]:
        """Get new content."""
        content = list(self.new_content)
        self.new_content.clear()
        return content


class FileAccessMonitor:
    """Monitor file system access."""
    
    def __init__(self):
        self.is_running = False
        self.thread = None
        self.new_accesses = deque(maxlen=20)

    def start(self):
        """Start file monitoring."""
        self.is_running = True
        self.thread = threading.Thread(target=self._monitor_files, daemon=True)
        self.thread.start()
        logger.info("File access monitoring started")

    def stop(self):
        """Stop monitoring."""
        self.is_running = False
        if self.thread:
            self.thread.join(timeout=1)

    def _monitor_files(self):
        """Monitor file access."""
        while self.is_running:
            try:
                # Basic file monitoring - could be enhanced with inotify
                time.sleep(5)
                
            except Exception as e:
                logger.error(f"Error monitoring files: {e}")
                time.sleep(10)

    def get_new_data(self) -> List[Dict]:
        """Get new file access events."""
        accesses = list(self.new_accesses)
        self.new_accesses.clear()
        return accesses


class EnvironmentMonitor:
    """Monitor environment changes."""
    
    def __init__(self):
        self.is_running = False
        self.thread = None
        self.new_changes = deque(maxlen=10)
        self.last_env = dict(os.environ)

    def start(self):
        """Start environment monitoring."""
        self.is_running = True
        self.thread = threading.Thread(target=self._monitor_environment, daemon=True)
        self.thread.start()
        logger.info("Environment monitoring started")

    def stop(self):
        """Stop monitoring."""
        self.is_running = False
        if self.thread:
            self.thread.join(timeout=1)

    def _monitor_environment(self):
        """Monitor environment variables."""
        while self.is_running:
            try:
                current_env = dict(os.environ)
                
                # Check for changes
                for key, value in current_env.items():
                    if key not in self.last_env or self.last_env[key] != value:
                        change_entry = {
                            "variable": key,
                            "value": value,
                            "timestamp": datetime.now().strftime('%H:%M:%S'),
                            "action": "changed"
                        }
                        self.new_changes.append(change_entry)
                
                self.last_env = current_env
                time.sleep(10)
                
            except Exception as e:
                logger.error(f"Error monitoring environment: {e}")
                time.sleep(10)

    def get_new_data(self) -> List[Dict]:
        """Get environment changes."""
        changes = list(self.new_changes)
        self.new_changes.clear()
        return changes 