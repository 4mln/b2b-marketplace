# app/db/base.py
# Define Base here to avoid circular imports
from sqlalchemy.orm import declarative_base

# Base class for models (needed for Alembic autogenerate)
Base = declarative_base()

# Re-export for backward compatibility
__all__ = ["Base"]
