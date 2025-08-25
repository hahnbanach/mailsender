from typing import Dict

from ..services.sendgrid_client import send_email


def send_generated_email(email_data: Dict) -> None:
    """Send generated email data using SendGrid."""
    send_email(
        recipient=email_data["recipient"],
        subject=email_data["subject"],
        body=email_data["body"],
        )
