"""
Configuration Manager - Handles application configuration
"""

import yaml
import json
import os
from pathlib import Path
from typing import Dict, Any, Optional


class ConfigManager:
    """Manages application configuration"""
    
    def __init__(self):
        self.config_dir = Path("config")
        self.config_dir.mkdir(exist_ok=True)
        self.config_file = self.config_dir / "settings.yaml"
        self.config: Dict[str, Any] = {}
        self.load_config()
    
    def load_config(self):
        """Load configuration from file"""
        if self.config_file.exists():
            try:
                with open(self.config_file, 'r') as f:
                    self.config = yaml.safe_load(f) or {}
            except Exception as e:
                print(f"Error loading config: {e}")
                self.config = {}
        else:
            self.create_default_config()
    
    def create_default_config(self):
        """Create default configuration"""
        default_config = {
            "app": {
                "name": "Pydantic AI Agent Framework",
                "version": "1.0.0",
                "debug": False,
                "host": "0.0.0.0",
                "port": 8000
            },
            "models": {
                "default_provider": "openai",
                "providers": {
                    "openai": {
                        "api_key_env": "OPENAI_API_KEY",
                        "models": [
                            "gpt-3.5-turbo",
                            "gpt-4",
                            "gpt-4-turbo-preview"
                        ]
                    },
                    "anthropic": {
                        "api_key_env": "ANTHROPIC_API_KEY",
                        "models": [
                            "claude-3-haiku-20240307",
                            "claude-3-sonnet-20240229",
                            "claude-3-opus-20240229"
                        ]
                    },
                    "gemini": {
                        "api_key_env": "GEMINI_API_KEY",
                        "models": [
                            "gemini-pro",
                            "gemini-pro-vision"
                        ]
                    }
                }
            },
            "database": {
                "type": "sqlite",
                "path": "data/agents.db"
            },
            "ui": {
                "theme": "light",
                "items_per_page": 10,
                "auto_save": True
            },
            "security": {
                "enable_auth": False,
                "session_timeout": 3600
            }
        }
        
        self.config = default_config
        self.save_config()
    
    def save_config(self):
        """Save configuration to file"""
        try:
            with open(self.config_file, 'w') as f:
                yaml.dump(self.config, f, default_flow_style=False, indent=2)
        except Exception as e:
            print(f"Error saving config: {e}")
    
    def get(self, key: str, default: Any = None) -> Any:
        """Get configuration value by key (supports dot notation)"""
        keys = key.split('.')
        value = self.config
        
        for k in keys:
            if isinstance(value, dict) and k in value:
                value = value[k]
            else:
                return default
        
        return value
    
    def set(self, key: str, value: Any):
        """Set configuration value by key (supports dot notation)"""
        keys = key.split('.')
        config = self.config
        
        for k in keys[:-1]:
            if k not in config:
                config[k] = {}
            config = config[k]
        
        config[keys[-1]] = value
        self.save_config()
    
    def get_model_config(self, provider: str) -> Optional[Dict]:
        """Get model configuration for a specific provider"""
        return self.get(f"models.providers.{provider}")
    
    def get_available_providers(self) -> list:
        """Get list of available model providers"""
        return list(self.get("models.providers", {}).keys())
    
    def is_provider_configured(self, provider: str) -> bool:
        """Check if a provider is properly configured"""
        provider_config = self.get_model_config(provider)
        if not provider_config:
            return False
        
        api_key_env = provider_config.get("api_key_env")
        if not api_key_env:
            return False
        
        return os.getenv(api_key_env) is not None
