import requests

from ..config.settings import settings

MR_CALL_BASE_URL = "https://api.mrcall.com"


def create_contact(phone_number: str, email: str, name: str = "") -> dict:
    """Create a contact in MrCall."""
    payload = {"phone_number": phone_number, "email": email, "name": name}
    auth = (settings.mrcall_user, settings.mrcall_password)
    response = requests.post(f"{MR_CALL_BASE_URL}/contacts", json=payload, auth=auth, timeout=10)
    response.raise_for_status()
    return response.json()


def start_call(contact_id: str) -> dict:
    """Trigger an outbound call via MrCall."""
    payload = {"business_id": settings.mrcall_business_id, "contact_id": contact_id}
    auth = (settings.mrcall_user, settings.mrcall_password)
    response = requests.post(f"{MR_CALL_BASE_URL}/calls", json=payload, auth=auth, timeout=10)
    response.raise_for_status()
    return response.json()
