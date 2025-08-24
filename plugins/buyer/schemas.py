from pydantic import BaseModel

class BuyerBase(BaseModel):
    name: str
    email: str

class BuyerCreate(BuyerBase):
    password: str

class BuyerUpdate(BuyerBase):
    password: str | None = None

class BuyerOut(BuyerBase):
    id: int

    model_config = {"from_attributes": True}  # Pydantic V2 compatible