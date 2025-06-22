"""
Pydantic AI Agent Framework - Main Application
A user-friendly web interface for managing AI agents using Pydantic AI
"""

import os
import json
import asyncio
from datetime import datetime
from typing import Dict, List, Optional, Any
from pathlib import Path

from fastapi import FastAPI, Request, Form, HTTPException, Depends
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
import uvicorn

from pydantic import BaseModel
from pydantic_ai import Agent
from pydantic_ai.models import OpenAIModel, AnthropicModel, GeminiModel

from utils.agent_manager import AgentManager
from utils.config_manager import ConfigManager
from utils.database import Database
from config.settings import Settings

# Initialize FastAPI app
app = FastAPI(
    title="Pydantic AI Agent Framework",
    description="A user-friendly interface for managing AI agents",
    version="1.0.0"
)

# Setup static files and templates
app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")

# Initialize managers
config_manager = ConfigManager()
agent_manager = AgentManager()
database = Database()
settings = Settings()

# Global state
active_agents: Dict[str, Agent] = {}
conversation_history: Dict[str, List[Dict]] = {}


class AgentConfig(BaseModel):
    """Agent configuration model"""
    name: str
    description: str
    system_prompt: str
    model_provider: str
    model_name: str
    temperature: float = 0.7
    max_tokens: int = 1000
    tools: List[str] = []
    enabled: bool = True


class ChatMessage(BaseModel):
    """Chat message model"""
    agent_id: str
    message: str
    user_id: str = "default"


@app.on_event("startup")
async def startup_event():
    """Initialize the application on startup"""
    print("🚀 Starting Pydantic AI Agent Framework...")
    
    # Create necessary directories
    os.makedirs("agents", exist_ok=True)
    os.makedirs("config", exist_ok=True)
    os.makedirs("logs", exist_ok=True)
    os.makedirs("data", exist_ok=True)
    
    # Initialize database
    await database.init_db()
    
    # Load existing agents
    await agent_manager.load_agents()
    
    print("✅ Application started successfully!")


@app.get("/", response_class=HTMLResponse)
async def dashboard(request: Request):
    """Main dashboard page"""
    agents = await agent_manager.get_all_agents()
    return templates.TemplateResponse(
        "dashboard.html", 
        {
            "request": request, 
            "agents": agents,
            "total_agents": len(agents),
            "active_agents": len([a for a in agents if a.get("enabled", False)])
        }
    )


@app.get("/agents", response_class=HTMLResponse)
async def agents_page(request: Request):
    """Agents management page"""
    agents = await agent_manager.get_all_agents()
    templates_list = await agent_manager.get_agent_templates()
    
    return templates.TemplateResponse(
        "agents.html",
        {
            "request": request,
            "agents": agents,
            "templates": templates_list,
            "model_providers": settings.get_available_models()
        }
    )


@app.get("/agent/{agent_id}", response_class=HTMLResponse)
async def agent_detail(request: Request, agent_id: str):
    """Individual agent detail page"""
    agent_config = await agent_manager.get_agent(agent_id)
    if not agent_config:
        raise HTTPException(status_code=404, detail="Agent not found")
    
    # Get conversation history for this agent
    history = conversation_history.get(agent_id, [])
    
    return templates.TemplateResponse(
        "agent_detail.html",
        {
            "request": request,
            "agent": agent_config,
            "conversation_history": history,
            "model_providers": settings.get_available_models()
        }
    )


@app.get("/chat/{agent_id}", response_class=HTMLResponse)
async def chat_interface(request: Request, agent_id: str):
    """Chat interface for specific agent"""
    agent_config = await agent_manager.get_agent(agent_id)
    if not agent_config:
        raise HTTPException(status_code=404, detail="Agent not found")
    
    return templates.TemplateResponse(
        "chat.html",
        {
            "request": request,
            "agent": agent_config,
            "conversation_history": conversation_history.get(agent_id, [])
        }
    )


@app.post("/api/agents")
async def create_agent(agent_config: AgentConfig):
    """Create a new agent"""
    try:
        agent_id = await agent_manager.create_agent(agent_config.dict())
        return {"success": True, "agent_id": agent_id, "message": "Agent created successfully"}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@app.put("/api/agents/{agent_id}")
async def update_agent(agent_id: str, agent_config: AgentConfig):
    """Update an existing agent"""
    try:
        await agent_manager.update_agent(agent_id, agent_config.dict())
        return {"success": True, "message": "Agent updated successfully"}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@app.delete("/api/agents/{agent_id}")
async def delete_agent(agent_id: str):
    """Delete an agent"""
    try:
        await agent_manager.delete_agent(agent_id)
        if agent_id in active_agents:
            del active_agents[agent_id]
        if agent_id in conversation_history:
            del conversation_history[agent_id]
        return {"success": True, "message": "Agent deleted successfully"}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@app.post("/api/agents/{agent_id}/toggle")
async def toggle_agent(agent_id: str):
    """Enable/disable an agent"""
    try:
        agent_config = await agent_manager.get_agent(agent_id)
        if not agent_config:
            raise HTTPException(status_code=404, detail="Agent not found")
        
        agent_config["enabled"] = not agent_config.get("enabled", False)
        await agent_manager.update_agent(agent_id, agent_config)
        
        return {
            "success": True, 
            "enabled": agent_config["enabled"],
            "message": f"Agent {'enabled' if agent_config['enabled'] else 'disabled'}"
        }
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@app.post("/api/chat")
async def chat_with_agent(chat_message: ChatMessage):
    """Send a message to an agent and get response"""
    try:
        agent_id = chat_message.agent_id
        message = chat_message.message
        
        # Get or create agent instance
        if agent_id not in active_agents:
            agent_config = await agent_manager.get_agent(agent_id)
            if not agent_config:
                raise HTTPException(status_code=404, detail="Agent not found")
            
            if not agent_config.get("enabled", False):
                raise HTTPException(status_code=400, detail="Agent is disabled")
            
            # Create agent instance
            active_agents[agent_id] = await agent_manager.create_agent_instance(agent_config)
        
        # Get agent instance
        agent = active_agents[agent_id]
        
        # Initialize conversation history if needed
        if agent_id not in conversation_history:
            conversation_history[agent_id] = []
        
        # Add user message to history
        user_message = {
            "role": "user",
            "content": message,
            "timestamp": datetime.now().isoformat()
        }
        conversation_history[agent_id].append(user_message)
        
        # Get agent response
        result = await agent.run(message)
        
        # Add agent response to history
        agent_message = {
            "role": "assistant",
            "content": result.data,
            "timestamp": datetime.now().isoformat(),
            "usage": result.usage().dict() if result.usage() else None
        }
        conversation_history[agent_id].append(agent_message)
        
        # Save conversation to database
        await database.save_conversation(agent_id, user_message, agent_message)
        
        return {
            "success": True,
            "response": result.data,
            "usage": result.usage().dict() if result.usage() else None
        }
        
    except Exception as e:
        return {"success": False, "error": str(e)}


@app.get("/api/agents/{agent_id}/history")
async def get_conversation_history(agent_id: str, limit: int = 50):
    """Get conversation history for an agent"""
    try:
        history = await database.get_conversation_history(agent_id, limit)
        return {"success": True, "history": history}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@app.get("/api/agents/{agent_id}/export")
async def export_agent_config(agent_id: str):
    """Export agent configuration"""
    try:
        agent_config = await agent_manager.get_agent(agent_id)
        if not agent_config:
            raise HTTPException(status_code=404, detail="Agent not found")
        
        return {
            "success": True,
            "config": agent_config,
            "export_date": datetime.now().isoformat()
        }
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@app.post("/api/agents/import")
async def import_agent_config(config_data: dict):
    """Import agent configuration"""
    try:
        # Validate and create agent from imported config
        agent_config = AgentConfig(**config_data["config"])
        agent_id = await agent_manager.create_agent(agent_config.dict())
        
        return {
            "success": True,
            "agent_id": agent_id,
            "message": "Agent imported successfully"
        }
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@app.get("/api/templates")
async def get_agent_templates():
    """Get available agent templates"""
    try:
        templates_list = await agent_manager.get_agent_templates()
        return {"success": True, "templates": templates_list}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@app.get("/api/models")
async def get_available_models():
    """Get available LLM models"""
    return {
        "success": True,
        "models": settings.get_available_models()
    }


@app.get("/api/stats")
async def get_system_stats():
    """Get system statistics"""
    try:
        agents = await agent_manager.get_all_agents()
        total_conversations = await database.get_total_conversations()
        
        return {
            "success": True,
            "stats": {
                "total_agents": len(agents),
                "active_agents": len([a for a in agents if a.get("enabled", False)]),
                "total_conversations": total_conversations,
                "uptime": "N/A"  # TODO: Implement uptime tracking
            }
        }
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


if __name__ == "__main__":
    print("🤖 Pydantic AI Agent Framework")
    print("===============================")
    print("Starting server...")
    
    uvicorn.run(
        "app:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )
