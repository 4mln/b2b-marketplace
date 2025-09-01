from logging.config import fileConfig
import asyncio

from sqlalchemy import pool, create_engine
from alembic import context

# Alembic Config object
config = context.config

# Logging setup
if config.config_file_name is not None:
    fileConfig(config.config_file_name)

# Import your SQLAlchemy models Base here
from app.db.base import Base
# Import models to ensure they are registered with Base.metadata
try:
    from plugins.seller.models import Seller
except ImportError:
    pass  # Seller models might not exist yet
target_metadata = Base.metadata

def run_migrations_offline() -> None:
    """Run migrations in 'offline' mode."""
    url = config.get_main_option("sqlalchemy.url")
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
    )

    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online() -> None:
    """Run migrations in 'online' mode with synchronous engine."""

    connectable = create_engine(
        config.get_main_option("sqlalchemy.url"),
        poolclass=pool.NullPool,
        future=True,
        echo=True,
    )

    with connectable.connect() as connection:
        context.configure(
            connection=connection,
            target_metadata=target_metadata,
            compare_type=True,
            render_as_batch=True
        )

        with context.begin_transaction():
            context.run_migrations()


def run_sync_migrations(connection):
    """Run migrations in sync mode inside async connection."""
    context.configure(
        connection=connection,
        target_metadata=target_metadata,
        compare_type=True,  # optional: detect column type changes
        render_as_batch=True  # optional: support SQLite ALTER TABLE, safe default
    )

    with context.begin_transaction():
        context.run_migrations()


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
