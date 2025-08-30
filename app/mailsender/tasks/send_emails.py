from typing import Iterable
import logging

from sqlalchemy.orm import Session

from ..db.models import Contact
from ..db.session import SessionLocal
from ..email import email_generator, email_sender


logger = logging.getLogger(__name__)


def send_emails(contacts: Iterable[Contact]) -> None:
    db: Session = SessionLocal()
    for contact in contacts:
        if contact.variables.get("opt_in") != "true":
            logger.debug("Contact %s has opted out; skipping email", contact.id)
            continue
        logger.debug("Contact %s has opted IN; sending email", contact.id)
        custom_args = (
            contact.custom_args if isinstance(contact.custom_args, dict) else {}
        )
        if custom_args != contact.custom_args:
            logger.debug(
                "Contact %s has invalid custom_args: %r", contact.id, contact.custom_args
            )
        campaign_id = custom_args.pop("campaign_id", None)
        if campaign_id is not None:
            logger.debug(
                "Removed campaign_id from custom_args for contact %s", contact.id
            )
        contact.custom_args = custom_args
        email_address = contact.emails[0]["address"] if contact.emails else ""
        body = email_generator.generate_email(
            email_address=email_address,
            custom_args=custom_args,
        )
        subject = f"Campaign {campaign_id}" if campaign_id else "Campaign"
        email_sender.send_generated_email(
            recipient=email_address, body=body, subject=subject
        )
        db.add(contact)
    db.commit()
    db.close()


def send_all_opt_in_contacts() -> None:
    db: Session = SessionLocal()
    contacts = (
        db.query(Contact)
        .filter(Contact.variables["opt_in"].as_string() == "true")
        .all()
    )
    db.close()
    send_emails(contacts)
