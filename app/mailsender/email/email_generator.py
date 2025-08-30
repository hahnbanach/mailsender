from typing import Dict

import json

import logging

from ..config.settings import settings
from ..services import openai_client

logger = logging.getLogger(__name__)


def generate_email(email_address: str, variables: Dict) -> str:
    """Generate email body using OpenAI based on contact info."""
    prompt = settings.email_prompt.format(
        email_address=email_address,
        variables=json.dumps(variables, ensure_ascii=False),
    )
    logger.debug("Prompt: %s", prompt)
    body = openai_client.generate_email(prompt)
    logger.debug("Generated body: %s", body)
    return body
