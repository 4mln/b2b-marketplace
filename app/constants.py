# app/constants.py
from enum import Enum as PyEnum

class SubscriptionType(str, PyEnum):
    FREE = "free"
    BASIC = "basic"
    PREMIUM = "premium"

class BadgeTypeEnum(str, PyEnum):
    FREE = "FREE"
    BASIC = "BASIC"
    PREMIUM = "PREMIUM"