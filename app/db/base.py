# app/db/base.py
from sqlalchemy.orm import declarative_base

# 1️⃣ Create the Base class
Base = declarative_base()

# 2️⃣ Import all models so SQLAlchemy knows about them
# Make sure these imports are **after** Base is created
from plugins.auth import models as auth_models
from plugins.seller import models as seller_models