from sqlalchemy import Column, Integer, Float, Boolean, String, DateTime, JSON, Enum as SQLAEnum, ForeignKey
from plugins.seller.models import Seller
from sqlalchemy.orm import relationship
from app.db.base import Base

class User(Base):
    __tablename__ = "users"
    __table_args__ = {"extend_existing": True}

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True, nullable=False)
    email = Column(String, unique=True, index=True, nullable=False)
    hashed_password = Column(String, nullable=False)
    is_active = Column(Boolean, default=True)
    is_superuser = Column(Boolean, default=False)

    # relationships
    sellers = relationship("Seller", back_populates="user", cascade="all, delete-orphan")
    buyer = relationship("Buyer", back_populates="user", uselist=False)
    gamification = relationship("UserBadge", back_populates="user", cascade="all, delete-orphan")
    carts = relationship("Cart", back_populates="user", cascade="all, delete-orphan")
    points = relationship("UserPoints", back_populates="user", cascade="all, delete-orphan")
    buyer_orders = relationship("Order", back_populates="buyer", cascade="all, delete-orphan")
    mobile_sessions = relationship("MobileAppSession", back_populates="user", cascade="all, delete-orphan")
    analytics_events = relationship("AnalyticsEvent", back_populates="user", cascade="all, delete-orphan")
    notifications = relationship("Notification", back_populates="user", cascade="all, delete-orphan")
    notification_preferences = relationship("UserNotificationPreference",  back_populates="user")
    notification_subscriptions = relationship("NotificationSubscription",back_populates="user",cascade="all, delete-orphan")
    wallet = relationship("Wallet",back_populates="user", uselist=False, cascade="all, delete-orphan")

