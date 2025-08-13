from typing import Iterable
from uuid import uuid4

from sqlalchemy.orm import Session

from ..db.models import Lead
from ..db.session import SessionLocal
from ..email import email_generator, email_sender


def _generate_pixel_id() -> str:
    return uuid4().hex


def send_emails(leads: Iterable[Lead]) -> None:
    db: Session = SessionLocal()
    for lead in leads:
        pixel_id = _generate_pixel_id()
        lead.pixel_url = pixel_id
        email_data = email_generator.generate_email(
            email_address=lead.email_address,
            other_info=lead.other_info or {},
            pixel_url=f"https://example.com/p/{pixel_id}",
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
