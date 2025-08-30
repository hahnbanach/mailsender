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
        variables = contact.variables or {}
        if variables.get("opt_in") != "true":
            logger.debug("Contact %s has opted out; skipping email", contact.contact_id)
            continue
        logger.debug("Contact %s has opted IN; sending email", contact.contact_id)
        emails = contact.emails or []
        email_address = emails[0]["address"] if emails else None
        if not email_address:
            logger.debug("Contact %s has no email; skipping", contact.contact_id)
            continue
        body = email_generator.generate_email(
            email_address=email_address,
            variables=variables,
        )
        email_sender.send_generated_email(
            recipient=email_address, body=body, subject="Campaign"
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
