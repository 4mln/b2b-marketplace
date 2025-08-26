from pydantic import BaseModel
from typing import List

class Notification(BaseModel):
    id: int
    user_id: int
    type: str  # e.g., email, in_app
    message: str
    read: bool = False

class NotificationResponse(BaseModel):
    notifications: List[Notification]