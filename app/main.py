from fastapi import FastAPI
from sqlalchemy.ext.asyncio import AsyncEngine
from app.core.config import settings
from app.core.db import engine  # make sure you export engine in db.py
from app.core.plugins import load_plugins

app = FastAPI(title="B2B Marketplace API")

@app.get("/")
async def root():
    return {"message": "API is running", "version": settings.APP_VERSION}

@app.on_event("startup")
async def startup_event():
    # Initialize plugins (register routes + init DB)
    await load_plugins(app, engine)

@app.on_event("shutdown")
async def shutdown_event():
    # If you want, plugins can have shutdown logic, or close DB connections here
    pass

