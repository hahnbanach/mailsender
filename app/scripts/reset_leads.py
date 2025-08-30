import os
import sys

sys.path.append(os.path.join(os.path.dirname(__file__), ".."))

from mailsender.db.models import Lead
from mailsender.db.session import SessionLocal


def reset_leads() -> None:
    db = SessionLocal()
    db.query(Lead).delete()
    db.commit()
    lead = Lead(
        email_address="mario@example.com",
        phone_number="+390221102420",
        opt_in="true",
        open_called=False,
        custom_args={"campaign_id": "sandbox_mode"},
    )
    db.add(lead)
    db.commit()
    db.close()


if __name__ == "__main__":
    reset_leads()
    print("Lead table reset")
