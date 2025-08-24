from sqlalchemy import Column, Integer, ForeignKey, DateTime, String, Enum
from sqlalchemy.orm import relationship
from datetime import datetime
from app.db.base import Base
from plugins.gamification.schemas import BadgeTypeEnum

# -----------------------------
# Badge table
# -----------------------------
class Badge(Base):
    __tablename__ = "badges"
    __table_args__ = {"extend_existing": True}

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    description = Column(String, nullable=True)
    type = Column(Enum(BadgeTypeEnum), default=BadgeTypeEnum.CUSTOM)
    points_required = Column(Integer, default=0)
    icon_url = Column(String, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)

# -----------------------------
# UserBadge table (association)
# -----------------------------
class UserBadge(Base):
    __tablename__ = "user_badges"
    __table_args__ = {"extend_existing": True}

    user_id = Column(Integer, ForeignKey("users.id"), primary_key=True)
    badge_id = Column(Integer, ForeignKey("badges.id"), primary_key=True)
    awarded_at = Column(DateTime, default=datetime.utcnow)

    user = relationship("User", back_populates="gamification")
    badge = relationship("Badge")

# -----------------------------
# UserPoints table
# -----------------------------
class UserPoints(Base):
    __tablename__ = "user_points"
    __table_args__ = {"extend_existing": True}

    user_id = Column(Integer, ForeignKey("users.id"), primary_key=True)
    points = Column(Integer, default=0)
    last_updated = Column(DateTime, default=datetime.utcnow)

    user = relationship("User", back_populates="points", uselist=False)