"""
Settings - Application settings and configuration
"""

import os
from typing import Dict, List, Any
from utils.config_manager import ConfigManager


class Settings:
    """Application settings"""
    
    def __init__(self):
        self.config_manager = ConfigManager()
    
    def get_available_models(self) -> Dict[str, List[str]]:
        """Get available models grouped by provider"""
        providers = self.config_manager.get("models.providers", {})
        available_models = {}
        
        for provider, config in providers.items():
            if self.config_manager.is_provider_configured(provider):
                available_models[provider] = config.get("models", [])
        
        return available_models
    
    def get_default_provider(self) -> str:
        """Get the default model provider"""
        return self.config_manager.get("models.default_provider", "openai")
    
    def get_app_config(self) -> Dict[str, Any]:
        """Get application configuration"""
        return self.config_manager.get("app", {})
    
    def get_database_config(self) -> Dict[str, Any]:
        """Get database configuration"""
        return self.config_manager.get("database", {})
    
    def get_ui_config(self) -> Dict[str, Any]:
        """Get UI configuration"""
        return self.config_manager.get("ui", {})
    
    def is_debug_mode(self) -> bool:
        """Check if debug mode is enabled"""
        return self.config_manager.get("app.debug", False)
    
    def get_host(self) -> str:
        """Get application host"""
        return self.config_manager.get("app.host", "0.0.0.0")
    
    def get_port(self) -> int:
        """Get application port"""
        return self.config_manager.get("app.port", 8000)
