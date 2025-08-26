from pydantic import BaseModel
from typing import List

class Price(BaseModel):
    product_id: int
    base_price: float
    discount: float = 0.0
    final_price: float
    currency: str = "USD"

class PriceResponse(BaseModel):
    prices: List[Price]