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
        custom_args = lead.custom_args if isinstance(lead.custom_args, dict) else {}
        if custom_args != lead.custom_args:
            logger.debug("Lead %s has invalid custom_args: %r", lead.id, lead.custom_args)
        if "campaign_id" in custom_args:
            custom_args.pop("campaign_id")
            logger.debug("Removed campaign_id from custom_args for lead %s", lead.id)
        lead.custom_args = custom_args
        email_data = email_generator.generate_email(
            email_address=lead.email_address,
            custom_args=custom_args,
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
