from sqlalchemy import Column, Integer, JSON, String
from sqlalchemy.orm import declarative_base

Base = declarative_base()


class Contact(Base):
    __tablename__ = "contact"

    id = Column(Integer, primary_key=True, index=True)
    business_id = Column(String, nullable=False)
    first = Column(String, nullable=True)
    last = Column(String, nullable=True)
    organizations = Column(JSON, default=list)
    emails = Column(JSON, default=list)
    variables = Column(JSON, default=dict)
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
