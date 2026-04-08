"""
Module: COMM_LINK (REFACTORED v2.0)
Purpose: FastAPI Web Server with GitHub Persistence
Owner: SIR BOSS
Architecture: Web-based communication with auto git commits
"""

import asyncio
import json
import logging
from datetime import datetime
from typing import Dict, List
from fastapi import FastAPI, WebSocket, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import aiohttp
from git import Repo
from config import (
    FASTAPI_HOST, FASTAPI_PORT, FASTAPI_DEBUG,
    GITHUB_REPO_OWNER, GITHUB_REPO_NAME, GITHUB_TOKEN,
    MEMORY_FILE, MEMORY_COMMIT_MESSAGE
)

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("COMM_LINK")

# FastAPI Application
app = FastAPI(title="ATLAS Communication Link", version="2.0")

# CORS Middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Request/Response Models
class ChatMessage(BaseModel):
    """Chat message model"""
    user: str
    message: str
    timestamp: str = None

class SystemCommand(BaseModel):
    """System command model"""
    command: str
    parameters: Dict = {}

class StatusResponse(BaseModel):
    """Status response model"""
    status: str
    message: str
    timestamp: str

class AtlasCommLinkV2:
    """
    Refactored Communication Link with FastAPI and GitHub persistence.
    """
    
    def __init__(self):
        """Initializes the web server and GitHub integration."""
        self.version = "ATLAS-CL-V2.0-FASTAPI"
        self.memory_file = MEMORY_FILE
        self.repo_owner = GITHUB_REPO_OWNER
        self.repo_name = GITHUB_REPO_NAME
        self.github_token = GITHUB_TOKEN
        
        logger.info(f"[{datetime.now()}] {self.version} Communication Link Online")
        
        # Initialize memory
        self.memory = self._load_memory()
        
        # Git repository
        try:
            self.repo = Repo(".")
            logger.info(f"GitHub repo initialized: {self.repo_owner}/{self.repo_name}")
        except Exception as e:
            logger.error(f"Failed to initialize GitHub repo: {e}")
            self.repo = None
    
    def _load_memory(self) -> Dict:
        """Loads memory from JSON file."""
        try:
            with open(self.memory_file, 'r') as f:
                return json.load(f)
        except FileNotFoundError:
            return {
                "version": self.version,
                "created": datetime.now().isoformat(),
                "messages": [],
                "decisions": [],
                "commands": []
            }
    
    def _save_memory(self):
        """Saves memory to JSON file."""
        with open(self.memory_file, 'w') as f:
            json.dump(self.memory, f, indent=2)
    
    async def commit_to_github(self, message: str = None):
        """
        Commits memory.json to GitHub repository.
        
        :param message: Custom commit message
        """
        if not self.repo:
            logger.error("GitHub repo not initialized")
            return False
        
        try:
            # Stage changes
            self.repo.index.add([self.memory_file])
            
            # Create commit message
            commit_msg = message or MEMORY_COMMIT_MESSAGE
            commit_msg += f" at {datetime.now().isoformat()}"
            
            # Commit
            self.repo.index.commit(commit_msg)
            
            # Push to GitHub
            origin = self.repo.remote(name='origin')
            origin.push()
            
            logger.info(f"Committed to GitHub: {commit_msg}")
            return True
        except Exception as e:
            logger.error(f"GitHub commit failed: {e}")
            return False
    
    async def log_message(self, user: str, message: str) -> Dict:
        """
        Logs a chat message and triggers GitHub commit.
        
        :param user: User name
        :param message: Message content
        :return: Logged message data
        """
        msg_data = {
            "timestamp": datetime.now().isoformat(),
            "user": user,
            "message": message
        }
        
        self.memory["messages"].append(msg_data)
        self._save_memory()
        
        # Auto-commit to GitHub
        await self.commit_to_github(f"[CHAT] {user}: {message[:30]}...")
        
        logger.info(f"Message logged from {user}")
        return msg_data
    
    async def process_command(self, command_data: SystemCommand) -> Dict:
        """
        Processes system commands.
        
        :param command_data: SystemCommand object
        :return: Command result
        """
        result = {
            "command": command_data.command,
            "status": "received",
            "timestamp": datetime.now().isoformat(),
            "result": None
        }
        
        # Log command
        self.memory["commands"].append(result)
        self._save_memory()
        
        # Process based on command type
        if command_data.command == "system_check":
            result["result"] = await self._system_check()
            result["status"] = "success"
        
        elif command_data.command == "get_memory":
            result["result"] = self.memory
            result["status"] = "success"
        
        elif command_data.command == "clear_memory":
            self.memory = self._load_memory()
            result["result"] = "Memory cleared"
            result["status"] = "success"
        
        else:
            result["status"] = "unknown"
            result["message"] = f"Unknown command: {command_data.command}"
        
        # Commit result to GitHub
        await self.commit_to_github(f"[COMMAND] {command_data.command}")
        
        return result
    
    async def _system_check(self) -> Dict:
        """Performs system health check."""
        return {
            "status": "healthy",
            "timestamp": datetime.now().isoformat(),
            "version": self.version,
            "brain_online": True,
            "vision_online": True,
            "hands_online": True
        }
    
    def shutdown_sequence(self):
        """Gracefully shutdown the communication link."""
        logger.info(f"[{datetime.now()}] COMM Link shutting down...")
        self._save_memory()

# ==================== FASTAPI ROUTES ====================

# Global instance
comm_link = AtlasCommLinkV2()

@app.get("/", response_model=StatusResponse)
async def root():
    """Root endpoint - system status."""
    return StatusResponse(
        status="online",
        message=f"ATLAS Communication Link {comm_link.version}",
        timestamp=datetime.now().isoformat()
    )

@app.get("/health", response_model=StatusResponse)
async def health_check():
    """Health check endpoint."""
    system_status = await comm_link._system_check()
    return StatusResponse(
        status="healthy",
        message="All systems operational",
        timestamp=system_status["timestamp"]
    )

@app.post("/chat", response_model=Dict)
async def chat_endpoint(chat: ChatMessage):
    """
    Main chat endpoint. Receives messages and triggers GitHub sync.
    
    :param chat: ChatMessage containing user and message
    :return: Logged message data
    """
    if not chat.message or not chat.user:
        raise HTTPException(status_code=400, detail="User and message are required")
    
    result = await comm_link.log_message(chat.user, chat.message)
    return result

@app.post("/command", response_model=Dict)
async def command_endpoint(cmd: SystemCommand):
    """
    System command endpoint.
    
    :param cmd: SystemCommand with command and parameters
    :return: Command execution result
    """
    if not cmd.command:
        raise HTTPException(status_code=400, detail="Command is required")
    
    result = await comm_link.process_command(cmd)
    return result

@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    """
    WebSocket endpoint for real-time communication.
    """
    await websocket.accept()
    logger.info("WebSocket client connected")
    
    try:
        while True:
            # Receive message
            data = await websocket.receive_text()
            msg_data = json.loads(data)
            
            # Log message
            result = await comm_link.log_message(
                msg_data.get("user", "unknown"),
                msg_data.get("message", "")
            )
            
            # Send confirmation
            await websocket.send_json({
                "status": "received",
                "data": result
            })
    except Exception as e:
        logger.error(f"WebSocket error: {e}")
    finally:
        logger.info("WebSocket client disconnected")

@app.get("/memory")
async def get_memory():
    """Retrieve system memory."""
    return comm_link.memory

@app.post("/memory/commit")
async def commit_memory(message: str = "Manual memory commit"):
    """Manually trigger GitHub commit."""
    success = await comm_link.commit_to_github(message)
    return {
        "status": "success" if success else "failed",
        "message": message,
        "timestamp": datetime.now().isoformat()
    }

@app.on_event("startup")
async def startup_event():
    """Initialize on startup."""
    logger.info("ATLAS COMM_LINK startup sequence initiated")

@app.on_event("shutdown")
async def shutdown_event():
    """Cleanup on shutdown."""
    comm_link.shutdown_sequence()
    logger.info("ATLAS COMM_LINK shutdown complete")

# ==================== MAIN ====================

if __name__ == "__main__":
    import uvicorn
    
    logger.info(f"Starting FastAPI server on {FASTAPI_HOST}:{FASTAPI_PORT}")
    logger.info(f"OpenAPI docs: http://{FASTAPI_HOST}:{FASTAPI_PORT}/docs")
    
    uvicorn.run(
        app,
        host=FASTAPI_HOST,
        port=FASTAPI_PORT,
        debug=FASTAPI_DEBUG
    )
