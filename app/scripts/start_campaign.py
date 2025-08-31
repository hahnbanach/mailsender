import argparse
import json
import logging
import os
import re
import sys
from openai import OpenAIError
from sqlalchemy import func
from sqlalchemy.orm import load_only

sys.path.append(os.path.join(os.path.dirname(__file__), ".."))

from mailsender.config.settings import settings
from mailsender.db.models import Contact
from mailsender.db.session import SessionLocal
from mailsender.services import openai_client
from mailsender.services.sendgrid_client import send_email
from mailsender.services.vonage_client import send_sms

logger = logging.getLogger(__name__)

_PLACEHOLDER_RE = re.compile(r"{([^{}]+)}")


def _resolve_path(data: object, path: str):
    """Resolve dotted path expressions like 'contact.first'."""
    current = data
    for part in path.split("."):
        if isinstance(current, dict):
            current = current.get(part)
        else:
            current = getattr(current, part, None)
        if current is None:
            return ""
    return current


def _apply_template(template: str, context: dict) -> str:
    def replacer(match: re.Match) -> str:
        key = match.group(1)
        value = _resolve_path(context, key)
        return "" if value is None else str(value)

    return _PLACEHOLDER_RE.sub(replacer, template)


def start_campaign(
    campaign_id: str, sender: str, body_ai: int, campaign_type: str = "email",
) -> None:
    logger.debug("Connecting to database: %s", settings.database_url)
    db = SessionLocal()
    try:
        total_contacts = db.query(func.count(Contact.id)).scalar()
        logger.debug("Database contains %d contacts", total_contacts)
    finally:
        db.close()

    if campaign_type == "sms":
        logger.info("Fetching contacts for campaign %s", campaign_id)
        db = SessionLocal()
        try:
            contacts = (
                db.query(Contact)
                .options(load_only(Contact.id, Contact.first, Contact.last, Contact.variables))
                .filter(
                    Contact.variables["campaign_id"].as_string() == campaign_id,
                    Contact.variables["opt_in"].as_string() == "true",
                )
                .all()
            )
            logger.info("Found %d contacts", len(contacts))
            for contact in contacts:
                variables = (
                    contact.variables if isinstance(contact.variables, dict) else {}
                )
                phone_number = variables.get("phone_number")
                if not phone_number:
                    logger.debug(
                        "Contact %s missing phone number; skipping SMS", contact.id
                    )
                    continue
                context = {"contact": contact}
                logger.debug("Using body template: %s", settings.body)
                body = _apply_template(settings.body, context)
                logger.debug("Templated SMS body: %s", body)
                try:
                    send_sms(recipient=phone_number, text=body, campaign_id=campaign_id)
                    logger.info("SMS sent to %s", phone_number)
                    variables["sms_sent"] = "true"
                    contact.variables = variables
                    db.commit()
                except Exception as exc:  # pragma: no cover - log external errors
                    logger.error("Error sending SMS to %s: %s", phone_number, exc)
                    db.rollback()
        finally:
            db.close()
    elif campaign_type == "email":
        logger.info("Fetching contacts for campaign %s", campaign_id)
        db = SessionLocal()
        try:
            contacts = (
                db.query(Contact)
                .options(
                    load_only(
                        Contact.id,
                        Contact.first,
                        Contact.last,
                        Contact.variables,
                        Contact.emails,
                    )
                )
                .filter(
                    Contact.variables["campaign_id"].as_string() == campaign_id,
                    Contact.variables["opt_in"].as_string() == "true",
                )
                .all()
            )
        finally:
            db.close()
        logger.info("Found %d contacts", len(contacts))
        for contact in contacts:
            if contact.variables.get("opt_in") != "true":
                logger.debug(
                    "Contact %s has opted out; skipping email", contact.emails[0]["address"]
                )
                continue
            variables = (
                contact.variables if isinstance(contact.variables, dict) else {}
            )
            context = {"contact": contact}
            if body_ai:
                email_address = contact.emails[0]["address"] if contact.emails else ""
                prompt = settings.email_prompt.format(
                    email_address=email_address,
                    variables=json.dumps(variables, ensure_ascii=False),
                )
                logger.debug("Prompt: %s", prompt)
                try:
                    body = openai_client.generate_email(prompt)
                except OpenAIError as exc:
                    logger.error("OpenAI error for %s: %s", email_address, exc)
                    continue
                logger.debug("Generated body: %s", body)
            else:
                logger.debug("Using body template: %s", settings.body)
                body = _apply_template(settings.body, context)
                logger.debug("Templated body: %s", body)
            subject = f"Campaign {campaign_id}"
            email_address = contact.emails[0]["address"] if contact.emails else ""
            logger.debug(
                "Sending email to %s with subject %r and body %r",
                email_address,
                subject,
                body,
            )
            send_email(
                recipient=email_address,
                subject=subject,
                body=body,
                body_type="text/html",
                from_email=sender,
                from_name=settings.from_name,
                variables={"campaign_id": campaign_id},
                sandbox_mode=(campaign_id == "sandbox_mode"),
            )
            logger.info("Email sent to %s", email_address)
    else:
        logger.error("Unknown campaign type: %s", campaign_type)


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--id", required=True, help="Campaign ID")
    parser.add_argument("--sender", required=True, help="Sender email address")
    parser.add_argument("--body-ai", dest="body_ai", type=int, choices=[0, 1], default=1)
    parser.add_argument(
        "--ctype",
        dest="ctype",
        choices=["email", "sms"],
        default="email",
        help="Campaign type",
    )
    parser.add_argument(
        "-q",
        "--quiet",
        action="store_true",
        help="Silence logging",
    )
    args = parser.parse_args()

    if args.quiet:
        logging.basicConfig(level=logging.CRITICAL + 1, stream=sys.stderr)
    else:
        logging.basicConfig(level=logging.DEBUG, stream=sys.stderr)

    start_campaign(args.id, args.sender, args.body_ai, args.ctype)

