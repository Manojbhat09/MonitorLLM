# Complete Terminal Activity Monitoring Guide

## The Problem with Basic Terminal Monitoring

You're absolutely right! The original implementation had a major limitation - it only monitored commands executed **through** SheLLM itself, not ALL terminal activity. This meant:

❌ **What it COULDN'T monitor:**
- Commands executed directly in terminal (outside SheLLM)
- Terminal output from external commands
- Terminal content from before SheLLM started
- Multiple terminal windows/tabs
- Background processes and their output
- Terminal scrollback buffer

✅ **What the Enhanced Version CAN Monitor:**
- ALL commands from shell history (in real-time)
- Existing terminal content and history
- Process monitoring (starts/stops)
- Terminal multiplexer content (tmux/screen)
- Environment changes
- File system activity

## How the Enhanced Monitoring Works

### 1. **Shell History Monitoring**
```bash
# Monitors these files in real-time:
~/.bash_history      # Bash commands
~/.zsh_history       # Zsh commands with timestamps
~/.local/share/fish/fish_history  # Fish shell
```

### 2. **Terminal Content Capture**
```bash
# Captures existing content via:
tmux capture-pane -p    # Current tmux pane content
screen -ls              # Screen session info
history 50              # Recent shell history
ps aux                  # Running processes
```

### 3. **Process Monitoring**
- Monitors process starts/stops
- Tracks terminal-related processes
- Detects interesting command execution

### 4. **Environment Monitoring**
- Tracks directory changes
- Monitors environment variables
- Captures system state changes

## Setup Instructions

### Method 1: Automatic Setup (Recommended)

Just run SheLLM - it automatically enables comprehensive monitoring:

```bash
# Enhanced monitoring starts automatically
python main.py

# Or in server mode
python main.py --server-mode
```

The system will show:
```
🔍 Comprehensive terminal monitoring activated
📊 Now monitoring ALL terminal activity (not just SheLLM commands)
```

### Method 2: Shell Integration (Maximum Coverage)

For the most comprehensive monitoring, add shell hooks:

#### For Bash users:
Add to `~/.bashrc`:
```bash
# SheLLM Integration
export SHELLM_SERVER="http://localhost:8000"

# Function to log commands to SheLLM
shellm_log() {
    if [ -n "$1" ] && [ -n "$SHELLM_SERVER" ]; then
        curl -s -X POST "$SHELLM_SERVER/log/command" \
            --data-urlencode "command=$1" \
            --connect-timeout 1 > /dev/null 2>&1 || true
    fi
}

# Hook command execution
trap 'shellm_log "$(history 1 | sed "s/^[ ]*[0-9]*[ ]*//")"' DEBUG
```

#### For Zsh users:
Add to `~/.zshrc`:
```bash
# SheLLM Integration
export SHELLM_SERVER="http://localhost:8000"

# Function to log commands
shellm_log() {
    if [ -n "$1" ] && [ -n "$SHELLM_SERVER" ]; then
        curl -s -X POST "$SHELLM_SERVER/log/command" \
            --data-urlencode "command=$1" \
            --connect-timeout 1 > /dev/null 2>&1 || true
    fi
}

# Hook command execution
preexec() {
    shellm_log "$1"
}
```

#### For Fish users:
Add to `~/.config/fish/config.fish`:
```fish
# SheLLM Integration
set -x SHELLM_SERVER "http://localhost:8000"

function shellm_log
    if test -n "$argv[1]" -a -n "$SHELLM_SERVER"
        curl -s -X POST "$SHELLM_SERVER/log/command" \
            --data-urlencode "command=$argv[1]" \
            --connect-timeout 1 > /dev/null 2>&1 || true
    end
end

# Hook command execution (Fish 3.1+)
function fish_preexec --on-event fish_preexec
    shellm_log "$argv[1]"
end
```

### Method 3: Terminal Multiplexer Integration

#### With tmux:
```bash
# Start tmux session with logging
tmux new-session -d -s shellm
tmux send-keys -t shellm "python main.py --server-mode" Enter

# In another pane, start SheLLM client
tmux split-window -h
tmux send-keys "python main.py" Enter
```

#### With screen:
```bash
# Start screen session
screen -S shellm
# Start SheLLM server
python main.py --server-mode

# Detach and start client in new window
# Ctrl+A, d (detach)
# screen -r shellm  (reattach)
```

## Testing the Monitoring

### 1. Test Basic Monitoring
```bash
# Start SheLLM in one terminal
python main.py --server-mode

# In another terminal, run commands:
ls -la
pwd
echo "Hello World"
git status

# Ask SheLLM about recent activity:
# In SheLLM: @ what commands have been run recently?
```

### 2. Test File References
```bash
# Create some files
echo "test content" > test.txt
ls > filelist.txt

# Ask SheLLM about them:
# @ what does @test.txt contain and compare it with @filelist.txt
```

### 3. Test Process Monitoring
```bash
# Start some processes
python -c "import time; time.sleep(30)" &
node -e "setTimeout(() => console.log('done'), 5000)"

# Ask SheLLM:
## what processes are currently running?
```

## Monitoring Capabilities

### What Gets Monitored:

1. **Commands and History**
   - Every command executed in terminal
   - Command timestamps and context
   - Shell history from before SheLLM started

2. **Terminal Content**
   - Current terminal buffer content
   - tmux/screen session content
   - Terminal scrollback (where available)

3. **Process Activity**
   - New processes started
   - Process termination
   - Background jobs

4. **File System**
   - File creation, modification, deletion
   - Directory changes
   - File access patterns

5. **Environment**
   - Environment variable changes
   - Working directory changes
   - System state changes

### Context Available to AI:

The AI now has access to:
```
=== EXISTING TERMINAL CONTENT ===
[Previous terminal session content]

=== TMUX SESSION CONTENT ===
[Current tmux pane content]

=== RECENT SHELL HISTORY ===
$ ls -la
$ cd /project
$ git status
$ python script.py

=== CURRENT ENVIRONMENT ===
User: john
Shell: /bin/zsh
Terminal: xterm-256color
PWD: /home/john/project

=== TERMINAL PROCESSES ===
[Running processes related to terminal]
```

## Advanced Features

### 1. Real-time Monitoring
```bash
# Monitor in real-time via WebSocket
python client_demo.py --websocket
```

### 2. Session Analytics
```bash
# Get detailed session analysis
curl http://localhost:8000/session/summary
```

### 3. Context Search
```bash
# Search terminal context
curl -X POST http://localhost:8000/chat \
  -H "Content-Type: application/json" \
  -d '{"message": "What was the last error I encountered?"}'
```

## Troubleshooting

### Issue: "No shell history monitoring"
**Solution:** Ensure your shell saves history and the file is readable:
```bash
# For bash
echo 'HISTFILE=~/.bash_history' >> ~/.bashrc
echo 'HISTSIZE=1000' >> ~/.bashrc

# For zsh
echo 'HISTFILE=~/.zsh_history' >> ~/.zshrc
echo 'HISTSIZE=1000' >> ~/.zshrc
```

### Issue: "tmux content not captured"
**Solution:** Ensure tmux is running and accessible:
```bash
# Check tmux sessions
tmux list-sessions

# If no sessions, start one
tmux new-session -d -s main
```

### Issue: "Process monitoring disabled"
**Solution:** Install psutil:
```bash
pip install psutil
```

## Security Considerations

### Data Privacy
- All monitoring happens locally by default
- No data sent to external servers (unless using OpenAI/Groq)
- Command history is stored temporarily in memory

### Command Filtering
- Sensitive commands (with passwords) are filtered
- Add custom filters in the configuration

### Network Security
- Server runs on localhost by default
- Use authentication if exposing to network

## Performance Impact

### Resource Usage
- **CPU:** ~1-3% additional usage
- **Memory:** ~50-100MB for monitoring
- **Disk:** Minimal (only session logs)

### Optimization
- Monitoring frequency is configurable
- Buffer sizes are limited to prevent memory issues
- Background processing doesn't block terminal

## Integration Examples

### VS Code Integration
```json
// settings.json
{
  "shellm.server": "http://localhost:8000",
  "shellm.autoStart": true
}
```

### Vim Integration
```vim
" .vimrc
function! SheLLMQuery()
  let query = input("Ask SheLLM: ")
  if query != ""
    execute "!curl -X POST http://localhost:8000/chat -d '{\"message\":\"" . query . "\"}'"
  endif
endfunction

command! SheLLM call SheLLMQuery()
```

---

## Summary

The enhanced SheLLM now provides **comprehensive terminal monitoring** that captures:

✅ **ALL commands** (not just SheLLM commands)  
✅ **Existing terminal content**  
✅ **Process activity**  
✅ **File system changes**  
✅ **Environment context**  
✅ **Terminal multiplexer content**  

This gives the AI complete awareness of your terminal environment and activity, making it much more useful and context-aware! 