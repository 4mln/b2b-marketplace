# app/db/base.py
# Define Base here to avoid circular imports
from sqlalchemy.orm import declarative_base
import importlib
import pkgutil
import plugins  # your plugins package

# Base class for models (needed for Alembic autogenerate)
Base = declarative_base()

for _, module_name, _ in pkgutil.iter_modules(plugins.__path__):
    try:
        importlib.import_module(f"plugins.{module_name}.models")
    except ModuleNotFoundError:
        pass

# Re-export for backward compatibility
__all__ = ["Base"]
