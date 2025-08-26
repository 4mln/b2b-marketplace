from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from .models import AITask
from .schemas import AITaskCreate

async def init_tables(engine):
    async with engine.begin() as conn:
        await conn.run_sync(AITask.metadata.create_all)

# -----------------------------
# Create AI Task
# -----------------------------
async def create_ai_task(db: AsyncSession, task: AITaskCreate):
    ai_task = AITask(**task.dict(), status="pending")
    db.add(ai_task)
    await db.commit()
    await db.refresh(ai_task)
    return ai_task

# -----------------------------
# Get all AI tasks
# -----------------------------
async def get_ai_tasks(db: AsyncSession):
    result = await db.execute(select(AITask))
    return result.scalars().all()
