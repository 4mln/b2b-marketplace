"""Test Plugin Routes
Simple routes to verify plugin loading works
"""
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.db.session import get_db_sync

router = APIRouter()

@router.get("/test")
def test_endpoint(db: Session = Depends(get_db_sync)):
    """Test endpoint to verify plugin loading works"""
    return {"message": "Test plugin loaded successfully!"}