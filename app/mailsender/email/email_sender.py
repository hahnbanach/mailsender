from ..services.sendgrid_client import send_email


def send_generated_email(recipient: str, body: str, subject: str = "Campaign") -> None:
    """Send generated email body using SendGrid."""
    send_email(recipient=recipient, subject=subject, body=body)
