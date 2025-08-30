import os
import sys

sys.path.append(os.path.join(os.path.dirname(__file__), ".."))

from mailsender.db.models import Base, Contact
from mailsender.db.session import engine, SessionLocal


def create_tables() -> None:
    Base.metadata.create_all(bind=engine, tables=[Contact.__table__])
    db = SessionLocal()
    if not db.query(Contact).filter(Contact.contact_id == "1").first():
        contact = Contact(
            contact_id="1",
            business_id="dummy",
            first="Mario",
            last="Rossi",
            organizations=[{"title": "", "company": "Club Di Gaming E Sport", "department": ""}],
            emails=[{"address": "mario@example.com"}],
            variables={
                "address": "Via Roma 1",
                "phone_number": "+390221102420",
                "opt_in": "true",
                "phonecall_made": "false",
                "phonecall_answered": "false",
                "sms_sent": "false",
                "wa_sent": "false",
                "campaign_id": "sandbox_mode",
            },
        )
        db.add(contact)
        db.commit()
    db.close()


if __name__ == "__main__":
    create_tables()
    print("Contact table created")
