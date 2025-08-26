import argparse
import os
import sys

sys.path.append(os.path.join(os.path.dirname(__file__), "..", "src"))

from mailsender.db.models import Lead
from mailsender.db.session import SessionLocal
from mailsender.services.sendgrid_client import send_email


def send_campaign_emails(campaign_id: str) -> None:
    db = SessionLocal()
    leads = db.query(Lead).filter(
        Lead.custom_args["campaign_id"].as_string() == campaign_id
    ).all()
    db.close()
    for lead in leads:
        send_email(
            recipient=lead.email_address,
            subject="SG sandbox test" if campaign_id == "sandbox_mode" else f"Campaign {campaign_id}",
            body="Hello from sandbox" if campaign_id == "sandbox_mode" else f"Hello from campaign {campaign_id}",
            body_type="text/plain",
            from_email="test@yourdomain.com",
            from_name="SG Test",
            custom_args={"campaign_id": campaign_id},
            sandbox_mode=(campaign_id == "sandbox_mode"),
        )


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("campaign_id")
    args = parser.parse_args()
    send_campaign_emails(args.campaign_id)
