import argparse
import logging
import os
import sys

sys.path.append(os.path.join(os.path.dirname(__file__), ".."))

from mailsender.db.models import Lead
from mailsender.db.session import SessionLocal
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
        logger.debug("Sending email to %s", lead.email_address)
        send_email(
            recipient=lead.email_address,
            subject="SG sandbox test" if campaign_id == "sandbox_mode" else f"Campaign {campaign_id}",
            body="Hello from sandbox" if campaign_id == "sandbox_mode" else f"Hello from campaign {campaign_id}",
            body_type="text/plain",
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
        "-v",
        "--verbose",
        action="store_true",
        help="Enable debug logging",
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
    elif args.verbose:
        logging.basicConfig(level=logging.DEBUG, stream=sys.stderr)
    else:
        logging.basicConfig(level=logging.INFO, stream=sys.stderr)

    send_campaign_emails(args.id, args.sender)
