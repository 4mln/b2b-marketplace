# app/main.py
from fastapi import FastAPI
from sqlalchemy.ext.asyncio import create_async_engine
from app.core.config import settings
from app.core.plugins.loader import PluginLoader


app = FastAPI(title="B2B Marketplace")

# Create async database engine
engine = create_async_engine(settings.DATABASE_URL, echo=True)

# Startup event: load all plugins
@app.on_event("startup")
async def startup_event():
    loader = PluginLoader()          # no app or engine here
    await loader.load_all(app, engine)  # pass app and engine here
    loader.enable_hot_reload(app, engine)