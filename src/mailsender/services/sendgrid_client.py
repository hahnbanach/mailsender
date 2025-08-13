import requests

from ..config.settings import settings

SENDGRID_API_URL = "https://api.sendgrid.com/v3/mail/send"


def send_email(recipient: str, subject: str, html_body: str) -> None:
    """Send an HTML email using SendGrid."""
    payload = {
        "personalizations": [{"to": [{"email": recipient}]}],
        "from": {"email": "noreply@example.com"},
        "subject": subject,
        "content": [{"type": "text/html", "value": html_body}],
    }
    headers = {
        "Authorization": f"Bearer {settings.sendgrid_key}",
        "Content-Type": "application/json",
    }
    response = requests.post(SENDGRID_API_URL, json=payload, headers=headers, timeout=10)
    response.raise_for_status()
