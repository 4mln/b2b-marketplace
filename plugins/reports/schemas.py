# plugins/reports/schemas.py
from pydantic import BaseModel
from typing import List, Dict, Optional
from datetime import datetime

class ReportDataOut(BaseModel):
    key: str
    value: float

    model_config = {"from_attributes": True}

class ReportOut(BaseModel):
    id: int
    name: str
    type: str
    created_at: datetime
    data: List[ReportDataOut] = []

    model_config = {"from_attributes": True}

class ReportCreate(BaseModel):
    name: str
    type: str
    data: Optional[Dict[str, float]] = {}

class ReportListOut(BaseModel):
    items: List[ReportOut]
    total: int
