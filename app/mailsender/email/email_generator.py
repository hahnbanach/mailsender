import json
from typing import Dict

from ..config.settings import settings
from ..services import openai_client


def generate_email(email_address: str, custom_args: Dict) -> Dict:
    """Generate email content using OpenAI based on lead info."""
    prompt = settings.email_prompt.format(
        email_address=email_address, custom_args=custom_args
    )
    response_text = openai_client.generate_email(prompt)
    return json.loads(response_text)
