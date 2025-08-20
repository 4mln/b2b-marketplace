# app/core/db.py
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker, declarative_base
from app.core.config import settings

# Async engine
engine = create_async_engine(
    settings.DATABASE_URL,
    future=True,
    echo=True
)

# Async session factory
AsyncSessionLocal = sessionmaker(
    bind=engine,
    class_=AsyncSession,
    expire_on_commit=False
)

# Base class for models (needed for Alembic autogenerate)
Base = declarative_base()

# Dependency to use in FastAPI routes
async def get_session() -> AsyncSession:
    async with AsyncSessionLocal() as session:
        yield session