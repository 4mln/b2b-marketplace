from pydantic import BaseModel
from typing import List

class UserActivity(BaseModel):
    user_id: int
    action: str
    timestamp: str

class UserActivityResponse(BaseModel):
    activities: List[UserActivity]