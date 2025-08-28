from sqlalchemy import Column, Integer, String, Boolean, DateTime
from sqlalchemy.orm import relationship
from app.db.base import Base

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True, nullable=False)
    full_name = Column(String, nullable=True)
    hashed_password = Column(String, nullable=False)
    is_active = Column(Boolean, default=True)
    is_superuser = Column(Boolean, default=False)
    kyc_status = Column(String, default="pending", nullable=False)  # pending, verified, rejected
    otp_code = Column(String, nullable=True)
    otp_expiry = Column(DateTime, nullable=True)
    id_document = Column(String, nullable=True)  # Path to uploaded ID document
    role = Column(String, default="user", nullable=False)  # user, seller, buyer

    # Relationships
    sellers = relationship(
        "Seller",
        back_populates="user",
        cascade="all, delete-orphan"
    )
    
    buyer = relationship(
        "Buyer",
        back_populates="user",
        cascade="all, delete-orphan",
        uselist=False
    )
    
    wallets = relationship(
        "Wallet",
        back_populates="user",
        cascade="all, delete-orphan"
    )