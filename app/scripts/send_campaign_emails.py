import argparse
import json
import logging
import os
import re
import sys

sys.path.append(os.path.join(os.path.dirname(__file__), ".."))

from mailsender.config.settings import settings
from mailsender.db.models import Lead
from mailsender.db.session import SessionLocal
from openai import OpenAIError
from mailsender.services import openai_client
from mailsender.services.sendgrid_client import send_email

logger = logging.getLogger(__name__)

_PLACEHOLDER_RE = re.compile(r"{([^{}]+)}")


def _apply_template(template: str, custom_args: dict) -> str:
    def replacer(match: re.Match) -> str:
        key = match.group(1)
        return str(custom_args.get(key, ""))

    return _PLACEHOLDER_RE.sub(replacer, template)


def send_campaign_emails(campaign_id: str, sender: str, body_ai: int) -> None:
    logger.info("Fetching leads for campaign %s", campaign_id)
    db = SessionLocal()
    try:
        leads = db.query(Lead).filter(
            Lead.custom_args["campaign_id"].as_string() == campaign_id
        ).all()
    finally:
        db.close()
    logger.info("Found %d leads", len(leads))
    for lead in leads:
        custom_args = lead.custom_args if isinstance(lead.custom_args, dict) else {}
        if "campaign_id" in custom_args:
            custom_args.pop("campaign_id")
        if body_ai == 0:
            prompt = settings.email_prompt.format(
                email_address=lead.email_address,
                custom_args=json.dumps(custom_args, ensure_ascii=False),
            )
            logger.debug("Prompt: %s", prompt)
            try:
                body = openai_client.generate_email(prompt)
            except OpenAIError as exc:
                logger.error("OpenAI error for %s: %s", lead.email_address, exc)
                continue
            logger.debug("Generated body: %s", body)
        else:
            logger.debug("Using body template: %s", settings.body)
            body = _apply_template(settings.body, custom_args)
            logger.debug("Templated body: %s", body)
        subject = f"Campaign {campaign_id}"
        logger.debug(
            "Sending email to %s with subject %r and body %r",
            lead.email_address,
            subject,
            body,
        )
        send_email(
            recipient=lead.email_address,
            subject=subject,
            body=body,
            body_type="text/html",
            from_email=sender,
            from_name="SG Test",
            custom_args={"campaign_id": campaign_id},
            sandbox_mode=(campaign_id == "sandbox_mode"),
        )
        logger.info("Email sent to %s", lead.email_address)


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--id", required=True, help="Campaign ID")
    parser.add_argument("--sender", required=True, help="Sender email address")
    parser.add_argument("--body-ai", dest="body_ai", type=int, choices=[0, 1], default=0)
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
