from abc import ABC, abstractmethod
from fastapi import FastAPI
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Dict, Any, Optional

class Plugin(ABC):
    """Base class for all plugins in the B2B marketplace."""
    
    def __init__(self, slug: str, name: str, description: str, version: str = "0.1.0"):
        """Initialize a new plugin.
        
        Args:
            slug: Unique identifier for the plugin
            name: Display name for the plugin
            description: Short description of the plugin's functionality
            version: Plugin version string
        """
        self.slug = slug
        self.name = name
        self.description = description
        self.version = version
        self.enabled = True
    
    @abstractmethod
    def register_routes(self, app: FastAPI, prefix: str = "/api/v1") -> None:
        """Register the plugin's routes with the FastAPI application.
        
        Args:
            app: The FastAPI application instance
            prefix: API route prefix
        """
        pass
    
    async def init_db(self, db: AsyncSession) -> None:
        """Initialize any database tables or data needed for the plugin.
        
        Args:
            db: Database session
        """
        pass
    
    async def startup(self, app: FastAPI) -> None:
        """Perform any startup tasks for the plugin.
        
        Args:
            app: The FastAPI application instance
        """
        pass
    
    async def shutdown(self, app: FastAPI) -> None:
        """Perform any cleanup tasks when the application is shutting down.
        
        Args:
            app: The FastAPI application instance
        """
        pass
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert plugin metadata to a dictionary.
        
        Returns:
            Dictionary containing plugin metadata
        """
        return {
            "slug": self.slug,
            "name": self.name,
            "description": self.description,
            "version": self.version,
            "enabled": self.enabled
        }