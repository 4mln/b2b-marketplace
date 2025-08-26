from sqlalchemy import Column, Integer, String, Float, DateTime, Boolean, ForeignKey, func
from sqlalchemy.orm import relationship
from sqlalchemy.orm import declarative_base

Base = declarative_base()  # or import centralized Base

class SubscriptionPlan(Base):
    __tablename__ = "subscription_plans"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False, unique=True)
    price = Column(Float, nullable=False)
    duration_days = Column(Integer, nullable=False)  # duration in days
    max_users = Column(Integer, nullable=True)  # optional limit
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

class UserSubscription(Base):
    __tablename__ = "user_subscriptions"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    plan_id = Column(Integer, ForeignKey("subscription_plans.id"), nullable=False)
    start_date = Column(DateTime(timezone=True), server_default=func.now())
    end_date = Column(DateTime(timezone=True), nullable=False)
    active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    plan = relationship("SubscriptionPlan")
