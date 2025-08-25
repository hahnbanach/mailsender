from sqlalchemy import Boolean, Column, Integer, JSON, String
from sqlalchemy.orm import declarative_base

Base = declarative_base()


class Lead(Base):
    __tablename__ = "lead"

    id = Column(Integer, primary_key=True, index=True)
    phone_number = Column(String, nullable=True)
    email_address = Column(String, unique=True, index=True, nullable=False)
    opt_in = Column(Boolean, default=True)
    other_info = Column(JSON, default=dict)
