import logging
import vonage

from ..config.settings import settings

logger = logging.getLogger(__name__)


def send_sms(recipient: str, text: str, *, sender: str | None = None) -> None:
    """Send an SMS using Vonage."""
    if not settings.vonage_api_key or not settings.vonage_api_secret:
        raise ValueError("Missing Vonage API credentials")
    from_name = sender or settings.sms_from
    if not from_name:
        raise ValueError("Missing SMS sender")
    client = vonage.Client(key=settings.vonage_api_key, secret=settings.vonage_api_secret)
    payload = {"from": from_name, "to": recipient, "text": text}
    logger.debug("Vonage SMS request: %s", payload)
    response = client.sms.send_message(payload)
    logger.debug("Vonage SMS response: %s", response)
    message = response["messages"][0]
    status = message.get("status")
    if status != "0":
        raise RuntimeError(message.get("error-text"))
