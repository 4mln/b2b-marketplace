from fastapi import FastAPI, APIRouter
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Dict, Any

from app.core.plugins.base import PluginBase as Plugin

class WalletPlugin(Plugin):
    """Wallet plugin for managing user wallets and transactions."""
    
    slug = "wallet"
    name = "Wallet"
    version = "0.1.0"
    description = "Manages user wallets, deposits, withdrawals, transfers, and cashback"
    
    def __init__(self, config=None):
        super().__init__(config=config)
    
    def register_routes(self, app: FastAPI) -> None:
        """Register the wallet routes with the FastAPI application."""
        from .routes import router as wallet_router  # Lazy import
        self.router = APIRouter(prefix=f"/api/v1/wallet", tags=["wallet"])
        self.router.include_router(wallet_router)
        app.include_router(self.router)
    
    async def init_db(self, engine) -> None:
        """Initialize any database tables or data needed for the wallet plugin."""
        # No initialization needed as tables are created by Alembic migrations
        pass
    
    async def on_startup(self, app: FastAPI) -> None:
        """Perform any startup tasks for the wallet plugin."""
        # No startup tasks needed
        pass
    
    async def on_shutdown(self, app: FastAPI) -> None:
        """Perform any cleanup tasks for the wallet plugin."""
        # No cleanup tasks needed
        pass
    
    def get_settings_schema(self) -> Dict[str, Any]:
        """Return the settings schema for the wallet plugin."""
        return {
            "type": "object",
            "properties": {
                "default_currency": {
                    "type": "string",
                    "default": "USD",
                    "description": "Default currency for new wallets"
                },
                "cashback_percentage": {
                    "type": "number",
                    "default": 1.0,
                    "description": "Default cashback percentage for transactions"
                },
                "withdrawal_fee_percentage": {
                    "type": "number",
                    "default": 0.5,
                    "description": "Fee percentage for withdrawals"
                },
                "min_withdrawal": {
                    "type": "number",
                    "default": 10.0,
                    "description": "Minimum withdrawal amount"
                },
                "supported_currencies": {
                    "type": "array",
                    "items": {"type": "string"},
                    "default": ["USD", "EUR", "BTC", "ETH"],
                    "description": "List of supported currencies"
                },
                "crypto_currencies": {
                    "type": "array",
                    "items": {"type": "string"},
                    "default": ["BTC", "ETH"],
                    "description": "List of supported crypto currencies"
                }
            },
            "required": ["default_currency", "supported_currencies"]
        }

# Create an instance of the plugin
plugin = WalletPlugin()