import logging
import requests

from ..config.settings import settings

SENDGRID_API_URL = "https://api.sendgrid.com/v3/mail/send"

logger = logging.getLogger(__name__)


def send_email(
    recipient: str,
    subject: str,
    body: str,
    *,
    from_email: str = "noreply@example.com",
    from_name: str | None = None,
    body_type: str = "text/html",
    sandbox_mode: bool = False,
) -> None:
    """Send an email using SendGrid."""
    payload = {
        "personalizations": [{"to": [{"email": recipient}]}],
        "from": {"email": from_email},
        "subject": subject,
        "tracking_settings":{"open_tracking":{"enable": True},
                             "subscription_tracking":{"enable":True}},
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
    logger.debug("SendGrid request: %s", payload)
    response = requests.post(SENDGRID_API_URL, json=payload, headers=headers, timeout=10)
    logger.debug("SendGrid response %s: %s", response.status_code, response.text)
    response.raise_for_status()
