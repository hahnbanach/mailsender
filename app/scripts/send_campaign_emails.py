import argparse
import json
import logging
import os
import re
import sys

sys.path.append(os.path.join(os.path.dirname(__file__), ".."))

from mailsender.config.settings import settings
from mailsender.db.models import Contact
from mailsender.db.session import SessionLocal
from openai import OpenAIError
from mailsender.services import openai_client
from mailsender.services.sendgrid_client import send_email

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


def send_campaign_emails(campaign_id: str, sender: str, body_ai: int) -> None:
    logger.info("Fetching contacts for campaign %s", campaign_id)
    db = SessionLocal()
    try:
        contacts = (
            db.query(Contact)
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


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--id", required=True, help="Campaign ID")
    parser.add_argument("--sender", required=True, help="Sender email address")
    parser.add_argument("--body-ai", dest="body_ai", type=int, choices=[0, 1], default=1)
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

    send_campaign_emails(args.id, args.sender, args.body_ai)
