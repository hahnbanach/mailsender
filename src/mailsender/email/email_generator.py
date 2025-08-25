import json
from typing import Dict

from ..config.settings import settings
from ..services import openai_client


def generate_email(email_address: str, other_info: Dict) -> Dict:
    """Generate email content using OpenAI based on lead info."""
    prompt = settings.email_prompt.format(
        email_address=email_address, other_info=other_info
    )
    response_text = openai_client.generate_email(prompt)
    return json.loads(response_text)
