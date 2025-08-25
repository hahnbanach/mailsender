import os
import sys

sys.path.append(os.path.join(os.path.dirname(__file__), "..", "src"))

from mailsender.db.models import Base, Campaign
from mailsender.db.session import engine


def create_tables() -> None:
    Base.metadata.create_all(bind=engine, tables=[Campaign.__table__])


if __name__ == "__main__":
    create_tables()
    print("Campaign table created")

