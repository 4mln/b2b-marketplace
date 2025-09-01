"""Test imports to verify that get_db_sync is properly defined"""

print("Testing imports...")

try:
    from app.db.session import get_db_sync
    print("Successfully imported get_db_sync from app.db.session")
except ImportError as e:
    print(f"Failed to import get_db_sync from app.db.session: {e}")

try:
    from app.core.db import get_db_sync
    print("Successfully imported get_db_sync from app.core.db")
except ImportError as e:
    print(f"Failed to import get_db_sync from app.core.db: {e}")

print("Import test complete.")