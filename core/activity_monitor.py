import os
import json
import time
import threading
import logging
import subprocess
from datetime import datetime, timedelta
from collections import deque
from pathlib import Path
from typing import Dict, List, Optional
import re

logger = logging.getLogger(__name__)

class TerminalActivityMonitor:
    def __init__(self, max_context_size=10000, max_history_items=100):
        self.max_context_size = max_context_size
        self.max_history_items = max_history_items
        self.command_history = deque(maxlen=max_history_items)
        self.output_history = deque(maxlen=max_history_items)
        self.context_buffer = ""
        self.current_directory = os.getcwd()
        self.session_start = datetime.now()
        self.file_references = {}
        self.lock = threading.Lock()
        
        # Initialize session data
        self.session_data = {
            "start_time": self.session_start.isoformat(),
            "commands": [],
            "outputs": [],
            "directory_changes": [],
            "file_operations": []
        }
        
        # Initialize comprehensive monitoring
        self.comprehensive_monitor = None
        self.is_comprehensive_monitoring = False
        
        logger.info("Terminal Activity Monitor initialized")
        
        # Try to start comprehensive monitoring
        self._try_start_comprehensive_monitoring()

    def _try_start_comprehensive_monitoring(self):
        """Try to start comprehensive terminal monitoring."""
        try:
            # Import the comprehensive monitor
            from .comprehensive_monitor import ComprehensiveTerminalMonitor
            
            self.comprehensive_monitor = ComprehensiveTerminalMonitor()
            self.comprehensive_monitor.start_monitoring()
            self.is_comprehensive_monitoring = True
            
            logger.info("🔍 Comprehensive terminal monitoring activated")
            logger.info("📊 Now monitoring ALL terminal activity (not just SheLLM commands)")
            
        except ImportError as e:
            logger.warning(f"Comprehensive monitoring not available: {e}")
            self._start_basic_monitoring()
        except Exception as e:
            logger.error(f"Error starting comprehensive monitoring: {e}")
            self._start_basic_monitoring()

    def _start_basic_monitoring(self):
        """Start basic monitoring as fallback."""
        try:
            # Monitor shell history file
            self._monitor_shell_history()
            logger.info("📋 Basic shell history monitoring started")
        except Exception as e:
            logger.error(f"Error starting basic monitoring: {e}")

    def _monitor_shell_history(self):
        """Monitor shell history file for new commands."""
        def monitor_history():
            history_file = self._get_shell_history_file()
            if not history_file or not os.path.exists(history_file):
                logger.warning("Shell history file not found")
                return
            
            last_size = os.path.getsize(history_file)
            
            while True:
                try:
                    current_size = os.path.getsize(history_file)
                    if current_size > last_size:
                        # Read new content
                        with open(history_file, 'r', encoding='utf-8', errors='ignore') as f:
                            f.seek(last_size)
                            new_lines = f.readlines()
                        
                        # Process new commands
                        for line in new_lines:
                            line = line.strip()
                            if line and not line.startswith('#'):
                                # Handle zsh history format
                                if line.startswith(': '):
                                    parts = line.split(';', 1)
                                    if len(parts) > 1:
                                        command = parts[1].strip()
                                    else:
                                        command = line
                                else:
                                    command = line
                                
                                if command:
                                    self.log_command(command, datetime.now())
                        
                        last_size = current_size
                    
                    time.sleep(2)  # Check every 2 seconds
                    
                except Exception as e:
                    logger.error(f"Error monitoring shell history: {e}")
                    time.sleep(5)
        
        # Start monitoring in background thread
        monitor_thread = threading.Thread(target=monitor_history, daemon=True)
        monitor_thread.start()

    def _get_shell_history_file(self) -> Optional[str]:
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

    def _get_existing_terminal_content(self) -> str:
        """Get existing terminal content from various sources."""
        content_parts = []
        
        # Try to get content from tmux
        try:
            result = subprocess.run(['tmux', 'capture-pane', '-p'], 
                                  capture_output=True, text=True, timeout=3)
            if result.returncode == 0:
                content_parts.append("=== TMUX SESSION CONTENT ===")
                content_parts.append(result.stdout)
        except (subprocess.TimeoutExpired, FileNotFoundError, subprocess.CalledProcessError):
            pass
        
        # Try to get content from screen
        try:
            result = subprocess.run(['screen', '-ls'], 
                                  capture_output=True, text=True, timeout=3)
            if result.returncode == 0 and 'Sockets' in result.stdout:
                content_parts.append("=== SCREEN SESSION ===")
                content_parts.append("Screen session detected")
        except (subprocess.TimeoutExpired, FileNotFoundError, subprocess.CalledProcessError):
            pass
        
        # Get shell history
        try:
            history_file = self._get_shell_history_file()
            if history_file and os.path.exists(history_file):
                with open(history_file, 'r', encoding='utf-8', errors='ignore') as f:
                    lines = f.readlines()
                
                # Get last 20 commands
                recent_history = []
                for line in lines[-20:]:
                    line = line.strip()
                    if line and not line.startswith('#'):
                        # Handle zsh history format
                        if line.startswith(': '):
                            parts = line.split(';', 1)
                            if len(parts) > 1:
                                command = parts[1].strip()
                            else:
                                command = line
                        else:
                            command = line
                        
                        if command:
                            recent_history.append(f"$ {command}")
                
                if recent_history:
                    content_parts.append("=== RECENT SHELL HISTORY ===")
                    content_parts.extend(recent_history)
        
        except Exception as e:
            logger.debug(f"Error getting shell history: {e}")
        
        # Get current environment info
        try:
            content_parts.append("=== CURRENT ENVIRONMENT ===")
            content_parts.append(f"User: {os.getenv('USER', 'unknown')}")
            content_parts.append(f"Shell: {os.getenv('SHELL', 'unknown')}")
            content_parts.append(f"Terminal: {os.getenv('TERM', 'unknown')}")
            content_parts.append(f"PWD: {os.getcwd()}")
            
            # Get running processes related to terminal
            try:
                result = subprocess.run(['ps', 'aux'], capture_output=True, text=True, timeout=3)
                if result.returncode == 0:
                    lines = result.stdout.split('\n')
                    terminal_processes = []
                    for line in lines:
                        if any(term in line.lower() for term in ['bash', 'zsh', 'fish', 'python', 'node', 'vim', 'nano']):
                            terminal_processes.append(line.strip())
                    
                    if terminal_processes:
                        content_parts.append("=== TERMINAL PROCESSES ===")
                        content_parts.extend(terminal_processes[:10])  # Show top 10
            except (subprocess.TimeoutExpired, subprocess.CalledProcessError):
                pass
                
        except Exception as e:
            logger.debug(f"Error getting environment info: {e}")
        
        return "\n".join(content_parts) if content_parts else ""

    def log_command(self, command: str, timestamp: Optional[datetime] = None):
        """Log a command execution."""
        if timestamp is None:
            timestamp = datetime.now()
        
        with self.lock:
            command_entry = {
                "timestamp": timestamp.isoformat(),
                "command": command,
                "directory": self.current_directory,
                "duration": None
            }
            
            self.command_history.append(command_entry)
            self.session_data["commands"].append(command_entry)
            
            # Update context buffer
            self._update_context_buffer(f"[{timestamp.strftime('%H:%M:%S')}] $ {command}")
            
            logger.debug(f"Logged command: {command}")

    def log_output(self, output: str, command: str = "", timestamp: Optional[datetime] = None):
        """Log command output."""
        if timestamp is None:
            timestamp = datetime.now()
        
        with self.lock:
            output_entry = {
                "timestamp": timestamp.isoformat(),
                "command": command,
                "output": output,
                "directory": self.current_directory
            }
            
            self.output_history.append(output_entry)
            self.session_data["outputs"].append(output_entry)
            
            # Update context buffer
            if output.strip():
                self._update_context_buffer(output)
            
            logger.debug(f"Logged output for command: {command}")

    def log_directory_change(self, new_directory: str, timestamp: Optional[datetime] = None):
        """Log directory changes."""
        if timestamp is None:
            timestamp = datetime.now()
        
        with self.lock:
            old_directory = self.current_directory
            self.current_directory = new_directory
            
            dir_change_entry = {
                "timestamp": timestamp.isoformat(),
                "from": old_directory,
                "to": new_directory
            }
            
            self.session_data["directory_changes"].append(dir_change_entry)
            self._update_context_buffer(f"[{timestamp.strftime('%H:%M:%S')}] cd {new_directory}")
            
            logger.debug(f"Directory changed: {old_directory} -> {new_directory}")

    def log_file_operation(self, operation: str, filepath: str, timestamp: Optional[datetime] = None):
        """Log file operations like create, edit, delete."""
        if timestamp is None:
            timestamp = datetime.now()
        
        with self.lock:
            file_op_entry = {
                "timestamp": timestamp.isoformat(),
                "operation": operation,
                "filepath": filepath,
                "directory": self.current_directory
            }
            
            self.session_data["file_operations"].append(file_op_entry)
            self._update_context_buffer(f"[{timestamp.strftime('%H:%M:%S')}] {operation}: {filepath}")
            
            logger.debug(f"File operation logged: {operation} {filepath}")

    def _update_context_buffer(self, text: str):
        """Update the context buffer, maintaining size limits."""
        self.context_buffer += text + "\n"
        
        # Trim context buffer if it exceeds max size
        if len(self.context_buffer) > self.max_context_size:
            lines = self.context_buffer.split('\n')
            # Keep the most recent lines
            while len('\n'.join(lines)) > self.max_context_size * 0.8:
                lines.pop(0)
            self.context_buffer = '\n'.join(lines)

    def get_context(self, include_recent_only: bool = False, minutes: int = 30) -> str:
        """Get the current terminal context."""
        # Use comprehensive monitoring if available
        if self.is_comprehensive_monitoring and self.comprehensive_monitor:
            try:
                return self.comprehensive_monitor.get_comprehensive_context(lines=100)
            except Exception as e:
                logger.error(f"Error getting comprehensive context: {e}")
                # Fall back to basic context
        
        # Get existing terminal content from various sources
        existing_content = self._get_existing_terminal_content()
        
        with self.lock:
            if include_recent_only:
                cutoff_time = datetime.now() - timedelta(minutes=minutes)
                recent_commands = [
                    cmd for cmd in self.command_history 
                    if datetime.fromisoformat(cmd["timestamp"]) >= cutoff_time
                ]
                recent_outputs = [
                    out for out in self.output_history 
                    if datetime.fromisoformat(out["timestamp"]) >= cutoff_time
                ]
                
                # Build recent context
                context_parts = []
                
                # Add existing terminal content
                if existing_content:
                    context_parts.append("=== EXISTING TERMINAL CONTENT ===")
                    context_parts.append(existing_content)
                    context_parts.append("")
                
                context_parts.append(f"Current directory: {self.current_directory}")
                context_parts.append(f"Recent activity (last {minutes} minutes):")
                
                # Interleave commands and outputs chronologically
                all_entries = []
                for cmd in recent_commands:
                    all_entries.append(("command", cmd))
                for out in recent_outputs:
                    all_entries.append(("output", out))
                
                all_entries.sort(key=lambda x: x[1]["timestamp"])
                
                for entry_type, entry in all_entries[-20:]:  # Last 20 entries
                    if entry_type == "command":
                        context_parts.append(f"$ {entry['command']}")
                    else:
                        output = entry['output'][:500] + "..." if len(entry['output']) > 500 else entry['output']
                        context_parts.append(output)
                
                return "\n".join(context_parts)
            else:
                context_parts = []
                
                # Add existing terminal content
                if existing_content:
                    context_parts.append("=== EXISTING TERMINAL CONTENT ===")
                    context_parts.append(existing_content)
                    context_parts.append("")
                
                context_parts.append(f"Current directory: {self.current_directory}")
                context_parts.append(self.context_buffer)
                
                return "\n".join(context_parts)

    def parse_file_references(self, message: str) -> Dict[str, str]:
        """Parse @file references in a message and return file contents."""
        file_contents = {}
        
        # Find all @filename or @/path/to/file references
        file_pattern = r'@([^\s@]+(?:\.[^\s@]*)?|/[^\s@]*)'
        matches = re.findall(file_pattern, message)
        
        for match in matches:
            filepath = match
            
            # Handle relative paths
            if not filepath.startswith('/'):
                filepath = os.path.join(self.current_directory, filepath)
            
            try:
                if os.path.isfile(filepath):
                    with open(filepath, 'r', encoding='utf-8', errors='ignore') as f:
                        content = f.read()
                        file_contents[match] = content
                        logger.debug(f"Loaded file content for: {match}")
                elif os.path.isdir(filepath):
                    # If it's a directory, list its contents
                    try:
                        contents = os.listdir(filepath)
                        file_contents[match] = f"Directory contents:\n" + "\n".join(contents)
                        logger.debug(f"Listed directory contents for: {match}")
                    except PermissionError:
                        file_contents[match] = f"Permission denied: {filepath}"
                else:
                    file_contents[match] = f"File not found: {filepath}"
                    logger.warning(f"File not found: {filepath}")
            except Exception as e:
                file_contents[match] = f"Error reading file: {str(e)}"
                logger.error(f"Error reading file {filepath}: {e}")
        
        return file_contents

    def get_session_summary(self) -> Dict:
        """Get a summary of the current session."""
        with self.lock:
            duration = datetime.now() - self.session_start
            
            return {
                "session_duration": str(duration),
                "total_commands": len(self.command_history),
                "total_outputs": len(self.output_history),
                "current_directory": self.current_directory,
                "directory_changes": len(self.session_data["directory_changes"]),
                "file_operations": len(self.session_data["file_operations"]),
                "most_used_commands": self._get_most_used_commands(),
                "recent_files": self._get_recent_files()
            }

    def _get_most_used_commands(self) -> List[tuple]:
        """Get most frequently used commands."""
        command_counts = {}
        for cmd_entry in self.command_history:
            cmd = cmd_entry["command"].split()[0] if cmd_entry["command"] else ""
            command_counts[cmd] = command_counts.get(cmd, 0) + 1
        
        return sorted(command_counts.items(), key=lambda x: x[1], reverse=True)[:10]

    def _get_recent_files(self) -> List[str]:
        """Get recently accessed files."""
        recent_files = []
        for file_op in list(self.session_data["file_operations"])[-10:]:
            if file_op["filepath"] not in recent_files:
                recent_files.append(file_op["filepath"])
        return recent_files

    def save_session(self, filepath: Optional[str] = None):
        """Save session data to file."""
        if filepath is None:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filepath = f"shellm_session_{timestamp}.json"
        
        with self.lock:
            try:
                with open(filepath, 'w') as f:
                    json.dump(self.session_data, f, indent=2, default=str)
                logger.info(f"Session saved to: {filepath}")
            except Exception as e:
                logger.error(f"Error saving session: {e}")

    def load_session(self, filepath: str):
        """Load session data from file."""
        try:
            with open(filepath, 'r') as f:
                self.session_data = json.load(f)
            
            # Rebuild command and output history
            self.command_history.clear()
            self.output_history.clear()
            
            for cmd in self.session_data.get("commands", []):
                self.command_history.append(cmd)
            
            for out in self.session_data.get("outputs", []):
                self.output_history.append(out)
            
            logger.info(f"Session loaded from: {filepath}")
        except Exception as e:
            logger.error(f"Error loading session: {e}")

    def cleanup_old_data(self, days: int = 7):
        """Clean up old session data."""
        cutoff_time = datetime.now() - timedelta(days=days)
        
        with self.lock:
            # Remove old commands
            self.command_history = deque([
                cmd for cmd in self.command_history 
                if datetime.fromisoformat(cmd["timestamp"]) >= cutoff_time
            ], maxlen=self.max_history_items)
            
            # Remove old outputs
            self.output_history = deque([
                out for out in self.output_history 
                if datetime.fromisoformat(out["timestamp"]) >= cutoff_time
            ], maxlen=self.max_history_items)
            
            logger.info(f"Cleaned up data older than {days} days") 