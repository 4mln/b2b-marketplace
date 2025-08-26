from sqlalchemy import Column, Integer, String, ForeignKey, Boolean, DateTime
from sqlalchemy.orm import relationship, declarative_base
from datetime import datetime

Base = declarative_base()

class SubscriptionPlan(Base):
    __tablename__ = "subscription_plans"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, unique=True, index=True)
    max_products = Column(Integer, default=10)
    max_orders = Column(Integer, default=100)
    price = Column(Integer, default=0)  # in cents or smallest currency unit
    duration_days = Column(Integer, default=30)
    active = Column(Boolean, default=True)

class UserSubscription(Base):
    __tablename__ = "user_subscriptions"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, index=True)  # link to Buyer or Seller later
    plan_id = Column(Integer, ForeignKey("subscription_plans.id"))
    start_date = Column(DateTime, default=datetime.utcnow)
    end_date = Column(DateTime)
    active = Column(Boolean, default=True)

    plan = relationship("SubscriptionPlan")