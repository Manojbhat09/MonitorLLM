import asyncio
import json
import logging
import os
from datetime import datetime
from typing import Dict, List, Optional
from fastapi import FastAPI, HTTPException, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import uvicorn
from contextlib import asynccontextmanager

from models.ollama_model import OllamaModel
from core.activity_monitor import TerminalActivityMonitor
from core.shellm import SheLLM

logger = logging.getLogger(__name__)

# Pydantic models for API requests/responses
class ChatRequest(BaseModel):
    message: str
    include_context: bool = True
    context_minutes: int = 30

class ChatResponse(BaseModel):
    response: str
    timestamp: str
    context_used: bool = False

class CommandRequest(BaseModel):
    prompt: str
    include_context: bool = True

class CommandResponse(BaseModel):
    command: str
    validated: bool
    timestamp: str

class ContextResponse(BaseModel):
    context: str
    timestamp: str
    directory: str

class SessionSummaryResponse(BaseModel):
    summary: Dict
    timestamp: str

class ServerConfig(BaseModel):
    host: str = "localhost"
    port: int = 8000
    ollama_host: str = "http://localhost:11434"
    ollama_model: str = "llama3.1"
    debug: bool = False

class SheLLMServer:
    def __init__(self, config: ServerConfig):
        self.config = config
        self.activity_monitor = TerminalActivityMonitor()
        self.ollama_model = OllamaModel(
            model_name=config.ollama_model,
            host=config.ollama_host
        )
        self.shellm = None
        self.websocket_connections: List[WebSocket] = []
        
        # Create FastAPI app
        self.app = FastAPI(
            title="SheLLM Server",
            description="Enhanced terminal AI assistant with activity monitoring",
            version="2.0.0",
            lifespan=self.lifespan
        )
        
        # Add CORS middleware
        self.app.add_middleware(
            CORSMiddleware,
            allow_origins=["*"],
            allow_credentials=True,
            allow_methods=["*"],
            allow_headers=["*"]
        )
        
        self.setup_routes()
        logger.info("SheLLM Server initialized")

    @asynccontextmanager
    async def lifespan(self, app: FastAPI):
        # Startup
        logger.info("Starting SheLLM Server...")
        yield
        # Shutdown
        logger.info("Shutting down SheLLM Server...")
        self.activity_monitor.save_session()

    def setup_routes(self):
        """Setup API routes."""
        
        @self.app.get("/health")
        async def health_check():
            return {"status": "healthy", "timestamp": datetime.now().isoformat()}

        @self.app.post("/chat", response_model=ChatResponse)
        async def chat(request: ChatRequest):
            """Enhanced chat endpoint with file reference support."""
            try:
                # Parse file references
                file_contents = self.activity_monitor.parse_file_references(request.message)
                
                # Get context if requested
                context = ""
                if request.include_context:
                    context = self.activity_monitor.get_context(
                        include_recent_only=True,
                        minutes=request.context_minutes
                    )
                
                # Generate response using Ollama
                response = self.ollama_model.chat_with_context(
                    context=context,
                    message=request.message,
                    file_contents=file_contents if file_contents else None
                )
                
                # Broadcast to WebSocket connections
                await self.broadcast_message({
                    "type": "chat_response",
                    "message": request.message,
                    "response": response,
                    "timestamp": datetime.now().isoformat()
                })
                
                return ChatResponse(
                    response=response,
                    timestamp=datetime.now().isoformat(),
                    context_used=request.include_context
                )
                
            except Exception as e:
                logger.error(f"Error in chat endpoint: {e}")
                raise HTTPException(status_code=500, detail=str(e))

        @self.app.post("/command", response_model=CommandResponse)
        async def generate_command(request: CommandRequest):
            """Generate shell command from natural language."""
            try:
                context = ""
                if request.include_context:
                    context = self.activity_monitor.get_context()
                
                command = self.ollama_model.get_command_suggestion(context, request.prompt)
                
                return CommandResponse(
                    command=command or "# Could not generate command",
                    validated=command is not None,
                    timestamp=datetime.now().isoformat()
                )
                
            except Exception as e:
                logger.error(f"Error generating command: {e}")
                raise HTTPException(status_code=500, detail=str(e))

        @self.app.get("/context", response_model=ContextResponse)
        async def get_context(recent_only: bool = False, minutes: int = 30):
            """Get current terminal context."""
            try:
                context = self.activity_monitor.get_context(
                    include_recent_only=recent_only,
                    minutes=minutes
                )
                
                return ContextResponse(
                    context=context,
                    timestamp=datetime.now().isoformat(),
                    directory=self.activity_monitor.current_directory
                )
                
            except Exception as e:
                logger.error(f"Error getting context: {e}")
                raise HTTPException(status_code=500, detail=str(e))

        @self.app.get("/session/summary", response_model=SessionSummaryResponse)
        async def get_session_summary():
            """Get session summary."""
            try:
                summary = self.activity_monitor.get_session_summary()
                
                return SessionSummaryResponse(
                    summary=summary,
                    timestamp=datetime.now().isoformat()
                )
                
            except Exception as e:
                logger.error(f"Error getting session summary: {e}")
                raise HTTPException(status_code=500, detail=str(e))

        @self.app.post("/log/command")
        async def log_command(command: str):
            """Log a command execution."""
            try:
                self.activity_monitor.log_command(command)
                
                # Broadcast to WebSocket connections
                await self.broadcast_message({
                    "type": "command_logged",
                    "command": command,
                    "timestamp": datetime.now().isoformat()
                })
                
                return {"status": "logged", "command": command}
                
            except Exception as e:
                logger.error(f"Error logging command: {e}")
                raise HTTPException(status_code=500, detail=str(e))

        @self.app.post("/log/output")
        async def log_output(command: str, output: str):
            """Log command output."""
            try:
                self.activity_monitor.log_output(output, command)
                
                # Broadcast to WebSocket connections  
                await self.broadcast_message({
                    "type": "output_logged",
                    "command": command,
                    "output": output,
                    "timestamp": datetime.now().isoformat()
                })
                
                return {"status": "logged", "command": command}
                
            except Exception as e:
                logger.error(f"Error logging output: {e}")
                raise HTTPException(status_code=500, detail=str(e))

        @self.app.post("/files/read")
        async def read_file_content(filepath: str):
            """Read file content for @file references."""
            try:
                file_contents = self.activity_monitor.parse_file_references(f"@{filepath}")
                
                if filepath in file_contents:
                    return {"filepath": filepath, "content": file_contents[filepath]}
                else:
                    raise HTTPException(status_code=404, detail="File not found")
                    
            except Exception as e:
                logger.error(f"Error reading file: {e}")
                raise HTTPException(status_code=500, detail=str(e))

        @self.app.websocket("/ws")
        async def websocket_endpoint(websocket: WebSocket):
            """WebSocket endpoint for real-time communication."""
            await websocket.accept()
            self.websocket_connections.append(websocket)
            
            try:
                while True:
                    # Receive messages from client
                    data = await websocket.receive_text()
                    message_data = json.loads(data)
                    
                    if message_data.get("type") == "ping":
                        await websocket.send_text(json.dumps({
                            "type": "pong",
                            "timestamp": datetime.now().isoformat()
                        }))
                    elif message_data.get("type") == "chat":
                        # Handle chat through WebSocket
                        request = ChatRequest(**message_data.get("data", {}))
                        response = await chat(request)
                        
                        await websocket.send_text(json.dumps({
                            "type": "chat_response",
                            "data": response.dict()
                        }))
                        
            except WebSocketDisconnect:
                logger.info("WebSocket client disconnected")
            except Exception as e:
                logger.error(f"WebSocket error: {e}")
            finally:
                if websocket in self.websocket_connections:
                    self.websocket_connections.remove(websocket)

    async def broadcast_message(self, message: Dict):
        """Broadcast message to all WebSocket connections."""
        if not self.websocket_connections:
            return
            
        message_str = json.dumps(message)
        disconnected = []
        
        for websocket in self.websocket_connections:
            try:
                await websocket.send_text(message_str)
            except Exception as e:
                logger.warning(f"Failed to send message to WebSocket: {e}")
                disconnected.append(websocket)
        
        # Remove disconnected WebSockets
        for websocket in disconnected:
            self.websocket_connections.remove(websocket)

    def run(self):
        """Run the server."""
        logger.info(f"Starting SheLLM server on {self.config.host}:{self.config.port}")
        uvicorn.run(
            self.app,
            host=self.config.host,
            port=self.config.port,
            log_level="debug" if self.config.debug else "info"
        )

# CLI integration
if __name__ == "__main__":
    import click
    
    @click.command()
    @click.option('--host', default='localhost', help='Host to bind to')
    @click.option('--port', default=8000, help='Port to bind to')
    @click.option('--ollama-host', default='http://localhost:11434', help='Ollama server host')
    @click.option('--ollama-model', default='llama3.1', help='Ollama model to use')
    @click.option('--debug', is_flag=True, help='Enable debug mode')
    def main(host, port, ollama_host, ollama_model, debug):
        config = ServerConfig(
            host=host,
            port=port,
            ollama_host=ollama_host,
            ollama_model=ollama_model,
            debug=debug
        )
        
        server = SheLLMServer(config)
        server.run()
    
    main() 