from typing import Dict

import json

from ..config.settings import settings
from ..services import openai_client


def generate_email(email_address: str, custom_args: Dict) -> str:
    """Generate email body using OpenAI based on lead info."""
    prompt = settings.email_prompt.format(
        email_address=email_address,
        custom_args=json.dumps(custom_args, ensure_ascii=False),
    )
    return openai_client.generate_email(prompt)
