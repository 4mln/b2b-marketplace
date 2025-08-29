from sqlalchemy import Column, Integer, String, ForeignKey, DateTime, Float, func, JSON
from sqlalchemy.orm import declarative_base, relationship


Base = declarative_base()


class RFQ(Base):
    __tablename__ = "rfqs"

    id = Column(Integer, primary_key=True, index=True)
    buyer_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    title = Column(String, nullable=False)
    specifications = Column(JSON, nullable=True)
    quantity = Column(Float, nullable=False)
    target_price = Column(Float, nullable=True)
    delivery = Column(String, nullable=True)
    expiry = Column(DateTime(timezone=True), nullable=True)
    attachments = Column(JSON, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    buyer = relationship("User")


class Quote(Base):
    __tablename__ = "quotes"

    id = Column(Integer, primary_key=True, index=True)
    rfq_id = Column(Integer, ForeignKey("rfqs.id"), nullable=False)
    seller_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    price = Column(Float, nullable=False)
    terms = Column(String, nullable=True)
    attachments = Column(JSON, nullable=True)
    status = Column(String, default="sent")  # sent, shortlisted, accepted, declined
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    rfq = relationship("RFQ")
    seller = relationship("User")


