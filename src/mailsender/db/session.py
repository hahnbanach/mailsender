from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from ..config.settings import settings

engine = create_engine(settings.database_url, echo=False, future=True)
SessionLocal = sessionmaker(bind=engine, autocommit=False, autoflush=False, future=True)
