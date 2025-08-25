import requests

from ..config.settings import settings

SENDGRID_API_URL = "https://api.sendgrid.com/v3/mail/send"


def send_email(
    recipient: str,
    subject: str,
    body: str,
    *,
    from_email: str = "noreply@example.com",
    from_name: str | None = None,
    body_type: str = "text/html",
    custom_args: dict | None = None,
    sandbox_mode: bool = False,
) -> None:
    """Send an email using SendGrid."""
    personalization = {"to": [{"email": recipient}]}
    if custom_args:
        personalization["custom_args"] = custom_args
    payload = {
        "personalizations": [personalization],
        "from": {"email": from_email},
        "subject": subject,
        "content": [{"type": body_type, "value": body}],
    }
    if from_name:
        payload["from"]["name"] = from_name
    if sandbox_mode:
        payload["mail_settings"] = {"sandbox_mode": {"enable": True}}
    headers = {
        "Authorization": f"Bearer {settings.sendgrid_key}",
        "Content-Type": "application/json",
    }
    response = requests.post(SENDGRID_API_URL, json=payload, headers=headers, timeout=10)
    response.raise_for_status()
