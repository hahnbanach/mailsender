from typing import Iterable
import logging

from sqlalchemy.orm import Session

from ..db.models import Lead
from ..db.session import SessionLocal
from ..email import email_generator, email_sender


logger = logging.getLogger(__name__)


def send_emails(leads: Iterable[Lead]) -> None:
    db: Session = SessionLocal()
    for lead in leads:
        if not lead.opt_in:
            logger.debug("Lead %s has opted out; skipping email", lead.id)
            continue
        custom_args = lead.custom_args if isinstance(lead.custom_args, dict) else {}
        if custom_args != lead.custom_args:
            logger.debug("Lead %s has invalid custom_args: %r", lead.id, lead.custom_args)
        campaign_id = custom_args.pop("campaign_id", None)
        if campaign_id is not None:
            logger.debug("Removed campaign_id from custom_args for lead %s", lead.id)
        lead.custom_args = custom_args
        body = email_generator.generate_email(
            email_address=lead.email_address,
            custom_args=custom_args,
        )
        subject = f"Campaign {campaign_id}" if campaign_id else "Campaign"
        email_sender.send_generated_email(
            recipient=lead.email_address, body=body, subject=subject
        )
        db.add(lead)
    db.commit()
    db.close()


def send_all_opt_in_leads() -> None:
    db: Session = SessionLocal()
    leads = db.query(Lead).filter(Lead.opt_in.is_(True)).all()
    db.close()
    send_emails(leads)
