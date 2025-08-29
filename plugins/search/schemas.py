from pydantic import BaseModel
from typing import List


class SavedSearchCreate(BaseModel):
    query: str


class SavedSearchOut(SavedSearchCreate):
    id: int
    user_id: int


class SearchResult(BaseModel):
    id: int
    name: str
    description: str | None = None
    price: float


class SearchResponse(BaseModel):
    items: List[SearchResult]


