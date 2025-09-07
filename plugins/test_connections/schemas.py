# plugins/test_connections/schemas.py
from pydantic import BaseModel
from datetime import datetime

class ConnectionTestOut(BaseModel):
    id: int
    name: str
    status: str
    checked_at: datetime

    model_config = ConfigDict(
        from_attributes = True
)

