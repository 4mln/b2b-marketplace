from pydantic import BaseModel
from datetime import datetime
from typing import Optional

class AITaskBase(BaseModel):
    name: str
    description: Optional[str] = None

class AITaskCreate(AITaskBase):
    user_id: int

class AITaskOut(AITaskBase):
    id: int
    user_id: int
    status: str
    created_at: datetime

    model_config = {"from_attributes": True}
