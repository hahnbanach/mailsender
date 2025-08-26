from sqlalchemy import Boolean, Column, Integer, JSON, String
from sqlalchemy.orm import declarative_base

Base = declarative_base()


class Lead(Base):
    __tablename__ = "lead"

    id = Column(Integer, primary_key=True, index=True)
    phone_number = Column(String, nullable=True)
    email_address = Column(String, unique=True, index=True, nullable=False)
    opt_in = Column(Boolean, default=True)
    custom_args = Column(JSON, default=dict)


class Campaign(Base):
    __tablename__ = "campaign"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, index=True, nullable=False)
    timestamp = Column(Integer, nullable=False)
    event = Column(String, nullable=False)
    sg_message_id = Column(String, nullable=True)
    smtp_id = Column("smtp_id", String, nullable=True)
    custom_args = Column(JSON, default=dict)
