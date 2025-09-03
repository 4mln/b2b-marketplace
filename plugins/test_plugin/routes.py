"""Test Plugin Routes
Simple routes to verify plugin loading works
"""
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

router = APIRouter()

@router.get("/test")
def test_endpoint(db: Session = Depends(lambda: __import__("importlib").import_module("app.db.session").get_db_sync)):
    """Test endpoint to verify plugin loading works"""
    return {"message": "Test plugin loaded successfully!"}