"""
Agent Manager - Handles creation, management, and lifecycle of AI agents
"""

import json
import uuid
import os
from datetime import datetime
from typing import Dict, List, Optional, Any
from pathlib import Path

from pydantic_ai import Agent
from pydantic_ai.models import OpenAIModel, AnthropicModel, GeminiModel
from pydantic import BaseModel


class AgentManager:
    """Manages AI agents and their configurations"""
    
    def __init__(self):
        self.agents_dir = Path("agents")
        self.templates_dir = Path("agents/templates")
        self.agents_dir.mkdir(exist_ok=True)
        self.templates_dir.mkdir(exist_ok=True)
        self.agents_cache: Dict[str, Dict] = {}
        
    async def load_agents(self):
        """Load all existing agents from disk"""
        try:
            for agent_file in self.agents_dir.glob("*.json"):
                if agent_file.name.startswith("template_"):
                    continue  # Skip template files
                    
                with open(agent_file, 'r') as f:
                    agent_config = json.load(f)
                    agent_id = agent_file.stem
                    self.agents_cache[agent_id] = agent_config
                    
            print(f"✅ Loaded {len(self.agents_cache)} agents")
        except Exception as e:
            print(f"❌ Error loading agents: {e}")
    
    async def get_all_agents(self) -> List[Dict]:
        """Get all agent configurations"""
        return list(self.agents_cache.values())
    
    async def get_agent(self, agent_id: str) -> Optional[Dict]:
        """Get a specific agent configuration"""
        return self.agents_cache.get(agent_id)
    
    async def create_agent(self, agent_config: Dict) -> str:
        """Create a new agent"""
        agent_id = str(uuid.uuid4())
        
        # Add metadata
        agent_config.update({
            "id": agent_id,
            "created_at": datetime.now().isoformat(),
            "updated_at": datetime.now().isoformat()
        })
        
        # Save to disk
        agent_file = self.agents_dir / f"{agent_id}.json"
        with open(agent_file, 'w') as f:
            json.dump(agent_config, f, indent=2)
        
        # Update cache
        self.agents_cache[agent_id] = agent_config
        
        return agent_id
    
    async def update_agent(self, agent_id: str, agent_config: Dict):
        """Update an existing agent"""
        if agent_id not in self.agents_cache:
            raise ValueError(f"Agent {agent_id} not found")
        
        # Preserve original metadata
        original_config = self.agents_cache[agent_id]
        agent_config.update({
            "id": agent_id,
            "created_at": original_config.get("created_at"),
            "updated_at": datetime.now().isoformat()
        })
        
        # Save to disk
        agent_file = self.agents_dir / f"{agent_id}.json"
        with open(agent_file, 'w') as f:
            json.dump(agent_config, f, indent=2)
        
        # Update cache
        self.agents_cache[agent_id] = agent_config
    
    async def delete_agent(self, agent_id: str):
        """Delete an agent"""
        if agent_id not in self.agents_cache:
            raise ValueError(f"Agent {agent_id} not found")
        
        # Remove from disk
        agent_file = self.agents_dir / f"{agent_id}.json"
        if agent_file.exists():
            agent_file.unlink()
        
        # Remove from cache
        del self.agents_cache[agent_id]
    
    async def create_agent_instance(self, agent_config: Dict) -> Agent:
        """Create a Pydantic AI agent instance from configuration"""
        try:
            # Get model based on provider
            model = self._get_model(agent_config)
            
            # Create agent with system prompt
            agent = Agent(
                model=model,
                system_prompt=agent_config.get("system_prompt", "You are a helpful AI assistant."),
            )
            
            # Add tools if specified
            tools = agent_config.get("tools", [])
            for tool_name in tools:
                tool_func = self._get_tool_function(tool_name)
                if tool_func:
                    agent.tool(tool_func)
            
            return agent
            
        except Exception as e:
            raise ValueError(f"Failed to create agent instance: {e}")
    
    def _get_model(self, agent_config: Dict):
        """Get the appropriate model instance based on configuration"""
        provider = agent_config.get("model_provider", "openai")
        model_name = agent_config.get("model_name", "gpt-3.5-turbo")
        temperature = agent_config.get("temperature", 0.7)
        max_tokens = agent_config.get("max_tokens", 1000)
        
        if provider == "openai":
            return OpenAIModel(
                model_name=model_name,
                temperature=temperature,
                max_tokens=max_tokens
            )
        elif provider == "anthropic":
            return AnthropicModel(
                model_name=model_name,
                temperature=temperature,
                max_tokens=max_tokens
            )
        elif provider == "gemini":
            return GeminiModel(
                model_name=model_name,
                temperature=temperature,
                max_tokens=max_tokens
            )
        else:
            raise ValueError(f"Unsupported model provider: {provider}")
    
    def _get_tool_function(self, tool_name: str):
        """Get tool function by name"""
        # This is where you would implement your custom tools
        # For now, return None for unsupported tools
        tools_map = {
            "web_search": self._web_search_tool,
            "calculator": self._calculator_tool,
            "file_reader": self._file_reader_tool,
        }
        
        return tools_map.get(tool_name)
    
    def _web_search_tool(self, query: str) -> str:
        """Example web search tool"""
        # Placeholder implementation
        return f"Web search results for: {query}"
    
    def _calculator_tool(self, expression: str) -> str:
        """Example calculator tool"""
        try:
            # Simple eval for basic math (in production, use a safer approach)
            result = eval(expression)
            return str(result)
        except:
            return "Invalid mathematical expression"
    
    def _file_reader_tool(self, file_path: str) -> str:
        """Example file reader tool"""
        try:
            with open(file_path, 'r') as f:
                return f.read()
        except:
            return "File not found or cannot be read"
    
    async def get_agent_templates(self) -> List[Dict]:
        """Get available agent templates"""
        templates = []
        
        # Load templates from templates directory
        for template_file in self.templates_dir.glob("*.json"):
            try:
                with open(template_file, 'r') as f:
                    template = json.load(f)
                    template["template_id"] = template_file.stem
                    templates.append(template)
            except Exception as e:
                print(f"Error loading template {template_file}: {e}")
        
        # If no templates exist, create default ones
        if not templates:
            await self._create_default_templates()
            templates = await self.get_agent_templates()
        
        return templates
    
    async def _create_default_templates(self):
        """Create default agent templates"""
        default_templates = [
            {
                "name": "General Assistant",
                "description": "A helpful general-purpose AI assistant",
                "system_prompt": "You are a helpful, harmless, and honest AI assistant. Provide clear, accurate, and helpful responses to user queries.",
                "model_provider": "openai",
                "model_name": "gpt-3.5-turbo",
                "temperature": 0.7,
                "max_tokens": 1000,
                "tools": [],
                "enabled": True
            },
            {
                "name": "Code Assistant",
                "description": "An AI assistant specialized in programming and software development",
                "system_prompt": "You are an expert software developer and programming assistant. Help users with coding questions, debugging, code review, and software architecture. Provide clear explanations and working code examples.",
                "model_provider": "openai",
                "model_name": "gpt-4",
                "temperature": 0.3,
                "max_tokens": 2000,
                "tools": ["file_reader"],
                "enabled": True
            },
            {
                "name": "Research Assistant",
                "description": "An AI assistant for research and information gathering",
                "system_prompt": "You are a research assistant that helps users find, analyze, and synthesize information. Provide well-researched, accurate, and comprehensive responses with proper citations when possible.",
                "model_provider": "openai",
                "model_name": "gpt-4",
                "temperature": 0.5,
                "max_tokens": 1500,
                "tools": ["web_search"],
                "enabled": True
            },
            {
                "name": "Math Tutor",
                "description": "An AI tutor specialized in mathematics",
                "system_prompt": "You are a patient and knowledgeable mathematics tutor. Help students understand mathematical concepts, solve problems step-by-step, and provide clear explanations. Encourage learning and build confidence.",
                "model_provider": "openai",
                "model_name": "gpt-3.5-turbo",
                "temperature": 0.4,
                "max_tokens": 1200,
                "tools": ["calculator"],
                "enabled": True
            }
        ]
        
        for i, template in enumerate(default_templates):
            template_file = self.templates_dir / f"template_{i+1}.json"
            with open(template_file, 'w') as f:
                json.dump(template, f, indent=2)
