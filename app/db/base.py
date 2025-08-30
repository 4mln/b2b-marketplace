# app/db/base.py
# Import Base from core db to avoid duplication
from app.core.db import Base

# Re-export for backward compatibility
__all__ = ["Base"]
