from typing import Iterable

from sqlalchemy.orm import Session

from ..db.models import Lead
from ..db.session import SessionLocal
from ..email import email_generator, email_sender


def send_emails(leads: Iterable[Lead]) -> None:
    db: Session = SessionLocal()
    for lead in leads:
        email_data = email_generator.generate_email(
            email_address=lead.email_address,
            custom_args=lead.custom_args or {},
        )
        email_sender.send_generated_email(email_data)
        db.add(lead)
    db.commit()
    db.close()


def send_all_opt_in_leads() -> None:
    db: Session = SessionLocal()
    leads = db.query(Lead).filter(Lead.opt_in.is_(True)).all()
    db.close()
    send_emails(leads)
