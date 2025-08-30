import logging
from vonage import Auth, Vonage
from vonage_sms import SmsMessage

from ..config.settings import settings

logger = logging.getLogger(__name__)


def send_sms(
    recipient: str,
    text: str,
    *,
    sender: str | None = None,
    campaign_id: str | None = None,
) -> None:
    """Send an SMS using Vonage."""
    if not settings.vonage_api_key or not settings.vonage_api_secret:
        raise ValueError("Missing Vonage API credentials")
    from_name = sender or settings.sms_from
    if not from_name:
        raise ValueError("Missing SMS sender")

    auth = Auth(
        api_key=settings.vonage_api_key,
        api_secret=settings.vonage_api_secret,
    )
    client = Vonage(auth=auth)
    message = SmsMessage(to=recipient, from_=from_name, text=text)
    if campaign_id:
        message.client_ref = campaign_id
    message.callback = settings.vonage_webhook
    logger.debug("Vonage SMS request: %s", message.model_dump(exclude_unset=True))
    response = client.sms.send(message)
    logger.debug("Vonage SMS response: %s", response.model_dump(exclude_unset=True))

    msg = response.messages[0]
    if msg.status != "0":
        raise RuntimeError(msg.error_text)
