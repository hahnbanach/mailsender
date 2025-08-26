import os
import sys

sys.path.append(os.path.join(os.path.dirname(__file__), ".."))

from mailsender.db.models import Base, Lead
from mailsender.db.session import engine, SessionLocal


def create_tables() -> None:
    Base.metadata.create_all(bind=engine, tables=[Lead.__table__])
    db = SessionLocal()
    if not db.query(Lead).filter(Lead.email_address == "mario@example.com").first():
        lead = Lead(
            email_address="mario@example.com",
            phone_number="+390221102420",
            opt_in=True,
            custom_args={"campaign_id": "sandbox_mode"},
        )
        db.add(lead)
        db.commit()
    db.close()


if __name__ == "__main__":
    create_tables()
    print("Lead table created")
