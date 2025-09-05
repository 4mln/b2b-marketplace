# plugins/test_connections/schemas.py
from pydantic import BaseModel
from datetime import datetime

class ConnectionTestOut(BaseModel):
    id: int
    name: str
    status: str
    checked_at: datetime

    class Config:
        from_attributes = True

