<h1 align="center">🚀 MonitorLLM </h1>
<h3 align="center">AI-Powered Terminal Assistant with Complete Activity Monitoring</h3>

<div align="center">

![GitHub License](https://img.shields.io/github/license/thereisnotime/SheLLM) 
![Python](https://img.shields.io/badge/python-3.8+-blue.svg)
![Ollama](https://img.shields.io/badge/🦙_Ollama-supported-green.svg)
![OpenAI](https://img.shields.io/badge/OpenAI-GPT--4-orange.svg)
![Status](https://img.shields.io/badge/status-production_ready-brightgreen.svg)

</div>

<div align="center">
  <h2>🔍 MONITORS ALL TERMINAL ACTIVITY • 🦙 LOCAL AI WITH OLLAMA • 🌐 HTTP/WebSocket API</h2>
</div>

<p align="center">
  <a href="https://skillicons.dev">
    <img src="https://skillicons.dev/icons?i=bash,linux,py,fastapi,docker" />
  </a>
</p>

---

## 🌟 **Revolutionary Terminal AI Experience**

SheLLM Enhanced is a **complete terminal AI assistant** that monitors ALL your terminal activity and provides intelligent assistance with **full context awareness**. Unlike basic AI tools, SheLLM knows what you've been doing, what files you're working with, and can reference any file or directory directly.

### ⚡ **What Makes SheLLM Enhanced Special:**

🔍 **COMPLETE TERMINAL MONITORING** - Captures ALL commands, outputs, and activity (not just its own)  
🦙 **LOCAL AI POWERED** - Uses Ollama for privacy-first, local AI processing  
📁 **FILE INTELLIGENCE** - Reference any file with `@filename` - AI reads and understands content  
🌐 **SERVER & API MODE** - HTTP/WebSocket APIs for integration with other tools  
💾 **SESSION ANALYTICS** - Detailed insights into your workflow and productivity  
🎯 **CONTEXT AWARE** - AI understands your terminal history, environment, and current state  

### 🎬 **See It In Action:**

```bash
# Ask about your terminal activity
@ what have I been working on today? Check @README.md for context

# Generate commands with full context
# find all python files that were modified today and run tests on them  

# Get intelligent analysis
## analyze my recent git commits and suggest improvements

# Reference multiple files
@ compare @package.json with @requirements.txt - what dependencies are different?
```

![Demo01](./assets/demo01.png)

*The AI has complete awareness of your terminal environment and activity*

## 📑 Table of Contents

- [🚀 Quick Start](#-quick-start)
- [💪 Core Features](#-core-features)
- [🔧 Installation](#-installation)
- [📖 Usage Guide](#-usage-guide)
- [🌐 Server & API Mode](#-server--api-mode)
- [🔍 Terminal Monitoring](#-terminal-monitoring)
- [📁 File Intelligence](#-file-intelligence)
- [⚙️ Configuration](#️-configuration)
- [🔌 Integrations](#-integrations)
- [📊 Analytics & Insights](#-analytics--insights)
- [🛡️ Security & Privacy](#️-security--privacy)
- [🤝 Contributing](#-contributing)

## 🚀 Quick Start

### ⚡ **30-Second Setup with Ollama (Recommended)**

```bash
# 1. Install Ollama (if not already installed)
curl -fsSL https://ollama.ai/install.sh | sh

# 2. Pull an AI model
ollama pull llama3.1

# 3. Clone and setup SheLLM Enhanced
git clone https://github.com/thereisnotime/SheLLM.git && cd SheLLM
python3 -m venv venv && source venv/bin/activate
pip install -r requirements.txt

# 4. Start with comprehensive monitoring
python main.py
```

**That's it!** SheLLM will automatically start monitoring ALL your terminal activity and provide AI assistance.

### 🎯 **Instant Usage Examples:**

```bash
# Generate commands with context awareness
# find all python files that have been modified today

# Ask questions about your terminal activity  
## what processes are currently running and which ones are using the most CPU?

# Reference files directly in conversation
@ what does @package.json contain and how does it compare to @requirements.txt?

# Get intelligent analysis of your work
@ analyze my recent git commits and suggest what I should work on next
```

### 🌐 **Server Mode for Integration:**

```bash
# Start as HTTP/WebSocket server
python main.py --server-mode

# Now access via API:
curl -X POST http://localhost:8000/chat \
  -H "Content-Type: application/json" \
  -d '{"message": "what files are in @/project?"}'
```

## 💪 Core Features

### 🔍 **Complete Terminal Monitoring**
- **ALL Command Tracking** - Monitors every command executed in your terminal (not just SheLLM commands)
- **Real-time Shell History** - Tracks bash, zsh, fish shell history as it happens
- **Process Monitoring** - Watches process starts, stops, and resource usage
- **Terminal Content Capture** - Captures tmux/screen session content and scrollback
- **Environment Awareness** - Tracks directory changes, environment variables, and system state

### 🦙 **Local AI with Ollama (Default)**
- **Privacy-First** - All AI processing happens locally on your machine
- **No API Keys Required** - Works completely offline with Ollama
- **Multiple Model Support** - Use llama3.1, codellama, mistral, or any Ollama model
- **Fast & Efficient** - Optimized for quick responses and low resource usage

### 📁 **File Intelligence System**
- **@File References** - Reference any file directly: `@ what does @config.py contain?`
- **Directory Browsing** - Explore directories: `@ show me the structure of @/project/src`
- **Multi-file Analysis** - Compare files: `@ compare @file1.py and @file2.py`
- **Smart Content Reading** - Handles text files, code, logs, configs automatically

### 🌐 **Server & API Mode**
- **HTTP REST API** - Full REST endpoints for all functionality
- **WebSocket Support** - Real-time bidirectional communication
- **Multi-client** - Support multiple concurrent connections
- **Cross-platform** - Works on Linux, macOS, Windows (WSL)
- **Integration Ready** - Easy to integrate with editors, IDEs, and other tools

### 🎯 **Advanced Context Awareness**
- **Session Memory** - Remembers everything from your terminal session
- **Smart Context** - Prioritizes recent and relevant activity
- **Command History Analysis** - Understands patterns in your workflow
- **Error Detection** - Identifies and helps resolve command failures
- **Workflow Insights** - Provides analytics on your productivity patterns

## 🔧 Installation

### 📋 **Prerequisites**

- **Python 3.8+** with pip
- **Ollama** (for local AI - recommended)
- **Terminal** (bash, zsh, fish, or PowerShell)

### 🏗️ **Installation Methods**

#### Method 1: Quick Install with Ollama (Recommended)

```bash
# Install Ollama
curl -fsSL https://ollama.ai/install.sh | sh

# Pull your preferred model
ollama pull llama3.1          # General purpose
ollama pull codellama:7b      # Code-focused  
ollama pull mistral          # Lightweight option

# Install SheLLM Enhanced
git clone https://github.com/thereisnotime/SheLLM.git
cd SheLLM
python -m venv venv
source venv/bin/activate     # Linux/Mac
# venv\Scripts\activate      # Windows
pip install -r requirements.txt
```

#### Method 2: With OpenAI/Groq APIs

```bash
# Clone repository
git clone https://github.com/thereisnotime/SheLLM.git
cd SheLLM

# Setup environment
python -m venv venv && source venv/bin/activate
pip install -r requirements.txt

# Configure API keys
cp .env.example .env
# Edit .env with your API keys:
# OPENAI_API_KEY=your_openai_key
# GROQ_API_KEY=your_groq_key
```

#### Method 3: Docker (Coming Soon)

```bash
# Pull the official image
docker pull shellm/enhanced:latest

# Run with volume mounting for file access
docker run -it -v $(pwd):/workspace shellm/enhanced:latest
```

## 📖 Usage Guide

### 🎮 **Interactive Mode Commands**

```bash
# Start SheLLM Enhanced (automatically enables monitoring)
python main.py

# Or specify different AI providers
python main.py --llm-api openai
python main.py --llm-api groq
python main.py --llm-api ollama --ollama-model codellama
```

#### **Command Types:**

| Prefix | Purpose | Example |
|--------|---------|---------|
| `#` | Generate shell commands | `# find all large files over 1GB` |
| `##` | Ask questions about terminal/system | `## what processes are using the most memory?` |
| `@` | Enhanced chat with file references | `@ what does @config.json contain?` |
| *(none)* | Execute commands normally | `ls -la`, `git status`, `npm install` |

### 🎯 **Real-World Usage Examples**

#### **Development Workflow**
```bash
# Start your development session
cd /my-project
git status

# Ask AI about your project with file context
@ analyze @package.json and @README.md - what kind of project is this?

# Generate commands with full context awareness
# run tests for all python files that were modified since last commit

# Get help with errors
## the last command failed - what went wrong and how can I fix it?

# Analyze your git history
@ review my recent commits in @.git and suggest what to work on next
```

#### **System Administration**
```bash
# Monitor system resources
top
df -h
ps aux

# Get AI insights about system state
## analyze current system performance and suggest optimizations

# Generate complex commands
# find all log files larger than 100MB that haven't been accessed in 30 days

# File system analysis
@ compare the contents of @/etc/hosts with @/etc/hostname
```

#### **File Management & Analysis**
```bash
# Create some files
echo "config data" > config.txt
ls > file_list.txt

# AI-powered file analysis
@ what's the difference between @config.txt and @config.bak?
@ analyze all files in @/project/logs and summarize any errors
@ check @Dockerfile and @docker-compose.yml for consistency
```

## 🌐 Server & API Mode

### 🚀 **Starting the Server**

```bash
# Start HTTP/WebSocket server
python main.py --server-mode

# Custom configuration
python main.py --server-mode \
  --server-host 0.0.0.0 \
  --server-port 8080 \
  --ollama-model codellama
```

### 📡 **HTTP API Endpoints**

| Method | Endpoint | Description |
|--------|----------|-------------|
| `GET` | `/health` | Health check |
| `GET` | `/context` | Get current terminal context |
| `GET` | `/session/summary` | Get session analytics |
| `POST` | `/chat` | Enhanced chat with file references |
| `POST` | `/command` | Generate shell command |
| `POST` | `/log/command` | Log command execution |
| `POST` | `/log/output` | Log command output |
| `POST` | `/files/read` | Read file content |

### 💻 **API Usage Examples**

#### **Chat with File References**
```bash
curl -X POST http://localhost:8000/chat \
  -H "Content-Type: application/json" \
  -d '{
    "message": "What does @package.json contain and how does it compare to @requirements.txt?",
    "include_context": true
  }'
```

#### **Generate Commands**
```bash
curl -X POST http://localhost:8000/command \
  -H "Content-Type: application/json" \
  -d '{
    "prompt": "find all log files modified in the last hour",
    "include_context": true
  }'
```

#### **Get Terminal Context**
```bash
curl http://localhost:8000/context?recent_only=true&minutes=30
```

### 🔌 **WebSocket Real-time Communication**

```javascript
const ws = new WebSocket('ws://localhost:8000/ws');

// Send chat message
ws.send(JSON.stringify({
  type: 'chat',
  data: {
    message: 'Analyze @config.py and suggest improvements',
    include_context: true
  }
}));

// Receive responses
ws.onmessage = (event) => {
  const response = JSON.parse(event.data);
  console.log('AI Response:', response);
};
```

### 🔧 **Client Integration**

Use the included demo client:

```bash
# Test HTTP API
python client_demo.py

# Test WebSocket
python client_demo.py --websocket
```

## 🔍 Terminal Monitoring

### 🎯 **What Gets Monitored**

SheLLM Enhanced provides **comprehensive terminal activity monitoring** that captures:

| Component | What's Monitored | Real-time |
|-----------|------------------|-----------|
| **Shell History** | All commands from bash/zsh/fish history files | ✅ Yes |
| **Process Activity** | Process starts, stops, resource usage | ✅ Yes |
| **Terminal Content** | tmux/screen sessions, terminal scrollback | ✅ Yes |
| **File Operations** | File creation, modification, deletion | ✅ Yes |
| **Environment** | Directory changes, env variables | ✅ Yes |

### 🔧 **How It Works**

```bash
# When you start SheLLM, you'll see:
🔍 Comprehensive terminal monitoring activated
📊 Now monitoring ALL terminal activity (not just SheLLM commands)
```

**Monitoring Sources:**
- **Shell History Files**: `~/.bash_history`, `~/.zsh_history`, `~/.local/share/fish/fish_history`
- **Process Monitoring**: Real-time process tracking with `psutil`
- **Terminal Multiplexers**: tmux session capture, screen detection
- **File System**: File access patterns and modifications
- **Environment**: Directory changes, shell state

### 📊 **Context Available to AI**

The AI receives comprehensive context including:

```
=== EXISTING TERMINAL CONTENT ===
[Content from before SheLLM started]

=== TMUX SESSION CONTENT ===
[Current tmux pane content if available]

=== RECENT SHELL HISTORY ===
$ git clone https://github.com/project/repo.git
$ cd repo
$ npm install
$ npm test

=== CURRENT ENVIRONMENT ===
User: developer
Shell: /bin/zsh
Terminal: xterm-256color
PWD: /home/developer/project

=== TERMINAL PROCESSES ===
[Active processes related to development]
```

### ⚙️ **Enhanced Shell Integration**

For maximum monitoring coverage, you can add shell hooks:

#### **Bash Integration**
```bash
# Add to ~/.bashrc
export SHELLM_SERVER="http://localhost:8000"

shellm_log() {
    if [ -n "$1" ] && [ -n "$SHELLM_SERVER" ]; then
        curl -s -X POST "$SHELLM_SERVER/log/command" \
            --data-urlencode "command=$1" \
            --connect-timeout 1 > /dev/null 2>&1 || true
    fi
}

trap 'shellm_log "$(history 1 | sed "s/^[ ]*[0-9]*[ ]*//")"' DEBUG
```

#### **Zsh Integration**
```bash
# Add to ~/.zshrc
preexec() {
    curl -s -X POST "http://localhost:8000/log/command" \
        --data-urlencode "command=$1" \
        --connect-timeout 1 > /dev/null 2>&1 || true
}
```

## 📁 File Intelligence

### 🎯 **@File Reference System**

SheLLM Enhanced introduces a revolutionary **@file reference system** that allows you to directly reference any file or directory in your conversations:

```bash
# Reference single files
@ what does @config.py contain?
@ explain the code in @src/main.py

# Reference directories
@ show me the structure of @/project/src
@ what files are in @./tests?

# Compare multiple files
@ compare @package.json with @requirements.txt - what dependencies are different?
@ analyze @Dockerfile and @docker-compose.yml for consistency issues

# Complex analysis
@ review @src/api.py and @tests/test_api.py - are the tests covering all the API endpoints?
```

### 🔧 **How File References Work**

When you use `@filename`, SheLLM:

1. **Locates the file** (supports relative and absolute paths)
2. **Reads the content** (handles text files, code, configs, logs)
3. **Provides full context** to the AI for analysis
4. **Handles large files** by summarizing when needed

### 📂 **Supported File Types**

| Category | Extensions | Example |
|----------|------------|---------|
| **Code** | `.py`, `.js`, `.go`, `.rs`, `.cpp`, `.java` | `@ refactor @app.py for better performance` |
| **Config** | `.json`, `.yaml`, `.toml`, `.ini`, `.conf` | `@ check @config.yaml for security issues` |
| **Documentation** | `.md`, `.txt`, `.rst` | `@ summarize @README.md in 3 sentences` |
| **Web** | `.html`, `.css`, `.xml` | `@ optimize @styles.css for loading speed` |
| **Data** | `.csv`, `.log`, `.sql` | `@ analyze @error.log for common patterns` |

## ⚙️ Configuration

### 🎛️ **Command Line Options**

```bash
# LLM Provider Selection
python main.py --llm-api ollama          # Local Ollama (default)
python main.py --llm-api openai          # OpenAI GPT-4
python main.py --llm-api groq            # Groq models

# Ollama Configuration
python main.py --ollama-host http://localhost:11434
python main.py --ollama-model codellama:7b

# Server Mode
python main.py --server-mode
python main.py --server-mode --server-host 0.0.0.0 --server-port 8080
```

### 📄 **Environment Configuration**

Create `.env` file for API-based providers:

```env
# OpenAI Configuration
OPENAI_API_KEY=your_openai_api_key

# Groq Configuration  
GROQ_API_KEY=your_groq_api_key

# Ollama Configuration (optional)
OLLAMA_HOST=http://localhost:11434
OLLAMA_MODEL=llama3.1
```

### ⚡ **Performance Tuning**

```env
# Monitor Configuration
TERMINAL_MONITOR_FREQUENCY=1000ms
CONTEXT_BUFFER_SIZE=10000
HISTORY_RETENTION_DAYS=7

# Server Configuration
SERVER_WORKERS=4
MAX_CONCURRENT_REQUESTS=10
WEBSOCKET_TIMEOUT=30
```

## 🔌 Integrations

### 🎨 **Editor Integrations**

#### **VS Code Extension**
```json
// settings.json
{
  "shellm.server": "http://localhost:8000",
  "shellm.autoStart": true,
  "shellm.fileReferences": true
}
```

#### **Vim/Neovim Plugin**
```vim
" .vimrc
function! SheLLMAnalyze()
  let filename = expand('%:p')
  execute "!curl -X POST http://localhost:8000/chat -d '{\"message\":\"analyze @" . filename . "\"}'"
endfunction

command! SheLLMAnalyze call SheLLMAnalyze()
nnoremap <leader>sa :SheLLMAnalyze<CR>
```

### 🐳 **Docker Integration**

```dockerfile
# Add to your Dockerfile
RUN pip install shellm-enhanced
COPY --from=shellm:latest /usr/local/bin/shellm /usr/local/bin/
ENV SHELLM_SERVER=http://shellm:8000
```

### 🔄 **CI/CD Integration**

#### **GitHub Actions**
```yaml
- name: Analyze with SheLLM
  run: |
    python -m shellm.analyze \
      --files "src/**/*.py" \
      --output analysis.md
```

#### **GitLab CI**
```yaml
shellm_analysis:
  script:
    - shellm analyze --project-root . --format json
  artifacts:
    reports:
      junit: shellm-analysis.xml
```

## 📊 Analytics & Insights

### 📈 **Session Analytics**

Get detailed insights about your terminal activity:

```bash
# Get session summary
curl http://localhost:8000/session/summary

# Example response:
{
  "session_duration": "2:30:45",
  "total_commands": 156,
  "total_processes": 23,
  "total_file_access": 89,
  "command_frequency": [
    ["git", 34],
    ["npm", 12], 
    ["python", 8]
  ],
  "productivity_insights": {
    "most_active_hour": "14:00-15:00",
    "primary_languages": ["python", "javascript"],
    "workflow_pattern": "development"
  }
}
```

### 🎯 **Workflow Insights**

SheLLM analyzes your patterns and provides insights:

- **Command Frequency**: Which commands you use most
- **File Access Patterns**: What files you work with
- **Productivity Metrics**: Active hours and focus time
- **Error Analysis**: Common failures and solutions
- **Project Context**: Understanding of your current work

### 📋 **Export & Reporting**

```bash
# Export session data
python main.py --export-session session_2024.json

# Generate productivity report
python main.py --generate-report --timeframe "last 7 days"

# Integration with time tracking
curl -X POST http://localhost:8000/analytics/export \
  --data '{"format": "csv", "timeframe": "month"}'
```

## 🛡️ Security & Privacy

### 🔐 **Privacy-First Design**

- **Local Processing**: Ollama runs entirely on your machine
- **No Data Collection**: No telemetry or usage analytics sent externally
- **Secure File Access**: Configurable file access restrictions
- **Command Filtering**: Automatic filtering of sensitive commands (passwords, keys)

### 🛡️ **Security Features**

```bash
# Command sanitization
SENSITIVE_PATTERNS=["password", "token", "key", "secret"]

# File access restrictions
ALLOWED_PATHS=["/home/user/projects", "/tmp"]
BLOCKED_PATHS=["/etc/passwd", "/root", "/home/*/.ssh"]

# Network security
SERVER_AUTH_TOKEN=your_secure_token
CORS_ORIGINS=["http://localhost:3000"]
```

### 🔒 **Best Practices**

1. **Use Ollama** for maximum privacy (no external API calls)
2. **Configure file restrictions** in production environments
3. **Use authentication** when exposing server to network
4. **Regular updates** to maintain security patches
5. **Monitor logs** for unusual activity

## 🤝 Contributing

We welcome contributions to SheLLM Enhanced! Here's how you can help:

### 🐛 **Bug Reports & Feature Requests**
- Open issues on GitHub with detailed descriptions
- Include system information and reproduction steps
- Suggest new features or improvements

### 💻 **Code Contributions**
- Fork the repository and create feature branches
- Follow the existing code style and patterns
- Add tests for new functionality
- Update documentation as needed

### 📝 **Documentation**
- Improve README and guides
- Add usage examples and tutorials
- Translate documentation to other languages

### 🧪 **Testing**
- Test on different operating systems
- Try various shell configurations
- Report compatibility issues

---

## 🌟 **Why SheLLM Enhanced?**

<div align="center">

| Feature | Basic Terminal AI | SheLLM Enhanced |
|---------|-------------------|-----------------|
| **Terminal Monitoring** | ❌ None | ✅ **Complete Activity Tracking** |
| **Context Awareness** | ❌ Limited | ✅ **Full Terminal History** |
| **File Intelligence** | ❌ No file access | ✅ **@File References** |
| **Privacy** | ⚠️ Cloud-dependent | ✅ **Local AI with Ollama** |
| **Integration** | ❌ Limited | ✅ **HTTP/WebSocket APIs** |
| **Analytics** | ❌ None | ✅ **Workflow Insights** |

</div>

<div align="center">
  <h2>🚀 <strong>Ready to revolutionize your terminal experience?</strong></h2>
  <p><strong>Start with Ollama for the ultimate privacy-first AI terminal assistant!</strong></p>
</div>

```bash
# Get started in 30 seconds
ollama pull llama3.1
git clone https://github.com/thereisnotime/SheLLM.git && cd SheLLM
pip install -r requirements.txt && python main.py
```

---

<div align="center">

**⭐ Star this repository if SheLLM Enhanced has improved your terminal workflow! ⭐**

[🐛 Report Bug](https://github.com/thereisnotime/SheLLM/issues) • [✨ Request Feature](https://github.com/thereisnotime/SheLLM/discussions) • [📚 Documentation](https://github.com/thereisnotime/SheLLM/wiki)

</div>
