from sqlalchemy.orm import Session
from .models import Buyer

def get_buyer(db: Session, buyer_id: int):
    return db.query(Buyer).filter(Buyer.id == buyer_id).first()

def create_buyer(db: Session, buyer_data: dict):
    buyer = Buyer(**buyer_data)
    db.add(buyer)
    db.commit()
    db.refresh(buyer)
    return buyer