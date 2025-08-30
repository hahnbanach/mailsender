import os
import sys

sys.path.append(os.path.join(os.path.dirname(__file__), ".."))

from mailsender.db.models import Contact
from mailsender.db.session import SessionLocal


def reset_contacts() -> None:
    db = SessionLocal()
    db.query(Contact).delete()
    db.commit()
    contact = Contact(
        business_id="dummy",
        first="Mario",
        last="Rossi",
        organizations=[
            {"title": "", "company": "Club Di Gaming E Sport", "department": ""}
        ],
        emails=[{"address": "mario@example.com"}],
        variables={
            "address": "",
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
    reset_contacts()
    print("Contact table reset")
