import argparse
import json
import logging
import os
import sys

sys.path.append(os.path.join(os.path.dirname(__file__), ".."))

from mailsender.config.settings import settings
from mailsender.db.models import Lead
from mailsender.db.session import SessionLocal
from mailsender.services import openai_client
from mailsender.services.sendgrid_client import send_email

logger = logging.getLogger(__name__)


def send_campaign_emails(campaign_id: str, sender: str) -> None:
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
        prompt = settings.email_prompt.format(
            email_address=lead.email_address, custom_args=custom_args
        )
        logger.debug("Prompt: %s", prompt)
        response_text = openai_client.generate_email(prompt)
        logger.debug("Generated text: %s", response_text)
        try:
            email_data = json.loads(response_text)
        except json.JSONDecodeError:
            logger.error(
                "OpenAI response not valid JSON for %s: %s",
                lead.email_address,
                response_text,
            )
            continue
        logger.debug("Email data: %s", email_data)
        logger.debug(
            "Sending email to %s with subject %r and body %r",
            lead.email_address,
            email_data.get("subject"),
            email_data.get("body"),
        )
        send_email(
            recipient=lead.email_address,
            subject=email_data.get("subject", f"Campaign {campaign_id}"),
            body=email_data.get("body", ""),
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

    send_campaign_emails(args.id, args.sender)
