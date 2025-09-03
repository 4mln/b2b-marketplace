from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List

from app.core.db import get_session
from . import schemas, crud

router = APIRouter()

# -----------------------------
# List all AI tasks
# -----------------------------
@router.get("/ai-tasks", response_model=List[schemas.AITaskOut])
async def list_ai_tasks(db: AsyncSession = Depends(lambda: __import__("importlib").import_module("app.db.session").get_session)):
    return await crud.get_ai_tasks(db)

# -----------------------------
# Create an AI task
# -----------------------------
@router.post("/ai-tasks", response_model=schemas.AITaskOut)
async def create_ai_task(task: schemas.AITaskCreate, db: AsyncSession = Depends(lambda: __import__("importlib").import_module("app.db.session").get_session)):
    return await crud.create_ai_task(db, task)

# -----------------------------
# Run AI assistant (experimental)
# -----------------------------
@router.post("/ai-assistant")
async def run_ai_assistant(prompt: str):
    # Placeholder: integrate AI model here
    response = f"AI response to: {prompt}"
    return {"prompt": prompt, "response": response}
