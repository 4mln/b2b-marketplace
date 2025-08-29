from sqlalchemy import Column, Integer, String, ForeignKey, DateTime, Float, Boolean, func, JSON
from sqlalchemy.orm import declarative_base, relationship


Base = declarative_base()


class Campaign(Base):
    __tablename__ = "ad_campaigns"

    id = Column(Integer, primary_key=True, index=True)
    owner_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    name = Column(String, nullable=False)
    budget = Column(Float, nullable=False)
    start_date = Column(DateTime(timezone=True), nullable=True)
    end_date = Column(DateTime(timezone=True), nullable=True)
    active = Column(Boolean, default=True)
    targeting = Column(JSON, nullable=True)  # {guild_ids:[], cities:[], tags:[]}
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    owner = relationship("User")


class Placement(Base):
    __tablename__ = "ad_placements"

    id = Column(Integer, primary_key=True, index=True)
    campaign_id = Column(Integer, ForeignKey("ad_campaigns.id"), nullable=False)
    type = Column(String, nullable=False)  # inapp_banner, sms, email, push, telegram, whatsapp
    budget_spent = Column(Float, default=0.0)
    metrics = Column(JSON, nullable=True)  # {impressions:..., clicks:...}
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    campaign = relationship("Campaign")


