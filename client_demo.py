#!/usr/bin/env python3
"""
SheLLM Client Demo

This script demonstrates how to interact with the SheLLM server
for terminal activity monitoring and AI assistance.
"""

import requests
import json
import time
import websocket
import threading
from typing import Dict, Any

class SheLLMClient:
    def __init__(self, base_url: str = "http://localhost:8000"):
        self.base_url = base_url
        self.session = requests.Session()
        
    def chat(self, message: str, include_context: bool = True) -> Dict[str, Any]:
        """Send a chat message with optional file references."""
        response = self.session.post(
            f"{self.base_url}/chat",
            json={
                "message": message,
                "include_context": include_context,
                "context_minutes": 30
            }
        )
        response.raise_for_status()
        return response.json()
    
    def generate_command(self, prompt: str) -> Dict[str, Any]:
        """Generate a shell command from natural language."""
        response = self.session.post(
            f"{self.base_url}/command",
            json={
                "prompt": prompt,
                "include_context": True
            }
        )
        response.raise_for_status()
        return response.json()
    
    def get_context(self, recent_only: bool = False, minutes: int = 30) -> Dict[str, Any]:
        """Get current terminal context."""
        response = self.session.get(
            f"{self.base_url}/context",
            params={
                "recent_only": recent_only,
                "minutes": minutes
            }
        )
        response.raise_for_status()
        return response.json()
    
    def log_command(self, command: str) -> Dict[str, Any]:
        """Log a command execution."""
        response = self.session.post(
            f"{self.base_url}/log/command",
            params={"command": command}
        )
        response.raise_for_status()
        return response.json()
    
    def log_output(self, command: str, output: str) -> Dict[str, Any]:
        """Log command output."""
        response = self.session.post(
            f"{self.base_url}/log/output",
            params={"command": command, "output": output}
        )
        response.raise_for_status()
        return response.json()
    
    def get_session_summary(self) -> Dict[str, Any]:
        """Get session summary."""
        response = self.session.get(f"{self.base_url}/session/summary")
        response.raise_for_status()
        return response.json()
    
    def read_file(self, filepath: str) -> Dict[str, Any]:
        """Read file content."""
        response = self.session.post(
            f"{self.base_url}/files/read",
            params={"filepath": filepath}
        )
        response.raise_for_status()
        return response.json()

def demo_basic_functionality():
    """Demonstrate basic SheLLM functionality."""
    print("🚀 SheLLM Client Demo")
    print("=" * 50)
    
    client = SheLLMClient()
    
    try:
        # Test health check
        response = client.session.get(f"{client.base_url}/health")
        print(f"✅ Server health: {response.json()}")
        
        # Simulate some terminal activity
        print("\n📝 Logging some terminal activity...")
        client.log_command("ls -la")
        client.log_output("ls -la", "total 24\ndrwxr-xr-x 5 user user 4096 Jan 15 10:30 .\ndrwxr-xr-x 3 user user 4096 Jan 15 10:25 ..")
        
        client.log_command("cd /tmp")
        client.log_command("echo 'Hello World' > test.txt")
        client.log_output("echo 'Hello World' > test.txt", "")
        
        print("✅ Commands logged successfully")
        
        # Get context
        print("\n📄 Getting terminal context...")
        context = client.get_context(recent_only=True, minutes=30)
        print(f"Current directory: {context['directory']}")
        print(f"Context preview: {context['context'][:200]}...")
        
        # Generate a command
        print("\n⚡ Generating command from natural language...")
        command_result = client.generate_command("find all python files in current directory")
        print(f"Generated command: {command_result['command']}")
        
        # Chat with file references
        print("\n💬 Chat with file references...")
        chat_result = client.chat("What files are in @/SheLLM and what does @README.md contain?")
        print(f"AI Response: {chat_result['response'][:300]}...")
        
        # Get session summary
        print("\n📊 Session summary...")
        summary = client.get_session_summary()
        print(f"Total commands: {summary['summary']['total_commands']}")
        print(f"Session duration: {summary['summary']['session_duration']}")
        print(f"Most used commands: {summary['summary']['most_used_commands'][:3]}")
        
        print("\n✅ Demo completed successfully!")
        
    except requests.exceptions.ConnectionError:
        print("❌ Error: Could not connect to SheLLM server.")
        print("Make sure the server is running with: python main.py --server-mode")
    except Exception as e:
        print(f"❌ Error: {e}")

def demo_websocket():
    """Demonstrate WebSocket functionality."""
    print("\n🌐 WebSocket Demo")
    print("=" * 30)
    
    def on_message(ws, message):
        data = json.loads(message)
        print(f"📨 Received: {data['type']}")
        if data['type'] == 'chat_response':
            print(f"🤖 AI: {data['data']['response'][:100]}...")
    
    def on_error(ws, error):
        print(f"❌ WebSocket error: {error}")
    
    def on_close(ws):
        print("🔌 WebSocket connection closed")
    
    def on_open(ws):
        print("✅ WebSocket connected")
        # Send a ping
        ws.send(json.dumps({"type": "ping"}))
        
        # Send a chat message
        time.sleep(1)
        ws.send(json.dumps({
            "type": "chat",
            "data": {
                "message": "Hello from WebSocket client!",
                "include_context": True
            }
        }))
    
    try:
        ws = websocket.WebSocketApp(
            "ws://localhost:8000/ws",
            on_message=on_message,
            on_error=on_error,
            on_close=on_close,
            on_open=on_open
        )
        
        # Run for 5 seconds
        ws.run_forever()
        
    except Exception as e:
        print(f"❌ WebSocket error: {e}")

if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="SheLLM Client Demo")
    parser.add_argument("--websocket", action="store_true", help="Run WebSocket demo")
    parser.add_argument("--server-url", default="http://localhost:8000", help="Server URL")
    
    args = parser.parse_args()
    
    if args.websocket:
        demo_websocket()
    else:
        demo_basic_functionality() 