from logging.config import fileConfig
import importlib
import pkgutil
import os
import plugins
import asyncio

from sqlalchemy import pool, create_engine
from sqlalchemy.ext.asyncio import create_async_engine
from alembic import context
from app.db.base import Base
from app.core.config import settings  # contains DATABASE_URL

# Alembic Config object
config = context.config

# Logging setup
if config.config_file_name is not None:
    fileConfig(config.config_file_name)

# Automatically import all models from all plugins only if models.py exists
for _, name, _ in pkgutil.iter_modules(plugins.__path__, plugins.__name__ + "."):
    try:
        plugin_path = os.path.join(os.path.dirname(__file__), "..", name.replace(".", "/"))
        models_file = os.path.join(plugin_path, "models.py")
        if os.path.isfile(models_file):
            importlib.import_module(f"{name}.models")
    except Exception:
        # skip any plugin that cannot be imported
        pass

# Set target metadata for Alembic
target_metadata = Base.metadata


def run_migrations_offline() -> None:
    """Run migrations in 'offline' mode."""
    sync_url = settings.DATABASE_URL.replace("asyncpg", "psycopg2")
    context.configure(
        url=sync_url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
    )
    with context.begin_transaction():
        context.run_migrations()


def run_sync_migrations(connection):
    """Run migrations in sync mode inside async connection."""
    context.configure(
        connection=connection,
        target_metadata=target_metadata,
        compare_type=True,
        render_as_batch=True
    )
    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online_sync() -> None:
    """Run migrations in 'online' mode with synchronous engine."""
    sync_url = settings.DATABASE_URL.replace("asyncpg", "psycopg2")
    connectable = create_engine(
        sync_url,
        poolclass=pool.NullPool,
        future=True,
        echo=True,
    )
    with connectable.connect() as connection:
        run_sync_migrations(connection)


async def run_migrations_online_async() -> None:
    """Run migrations in 'online' mode with async engine."""
    connectable = create_async_engine(
        settings.DATABASE_URL,
        poolclass=pool.NullPool,
        future=True,
        echo=True,
    )
    async with connectable.connect() as connection:
        await connection.run_sync(run_sync_migrations)
    await connectable.dispose()


# Execute the appropriate mode
if context.is_offline_mode():
    run_migrations_offline()
else:
    # Choose sync or async based on URL
    if settings.DATABASE_URL.startswith("postgresql+asyncpg"):
        asyncio.run(run_migrations_online_async())
    else:
        run_migrations_online_sync()
