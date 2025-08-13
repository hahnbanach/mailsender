from datetime import datetime
from sqlalchemy import Boolean, Column, DateTime, Integer, JSON, String
from sqlalchemy.orm import declarative_base

Base = declarative_base()


class Lead(Base):
    __tablename__ = "leads"

    id = Column(Integer, primary_key=True, index=True)
    email_address = Column(String, unique=True, index=True, nullable=False)
    phone_number = Column(String, nullable=True)
    opt_in = Column(Boolean, default=True)
    other_info = Column(JSON, default=dict)
    created_at = Column(DateTime, default=datetime.utcnow)
    pixel_url = Column(String, nullable=True)
    opened_at = Column(DateTime, nullable=True)
