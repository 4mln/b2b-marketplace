from sqlalchemy import Column, Integer, String, Text, DateTime, func
from sqlalchemy.orm import declarative_base


Base = declarative_base()


class Page(Base):
    __tablename__ = "cms_pages"

    id = Column(Integer, primary_key=True, index=True)
    slug = Column(String, unique=True, nullable=False)
    title = Column(String, nullable=False)
    content = Column(Text, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())


