import logging
from openai import OpenAI, OpenAIError

from ..config.settings import settings

logger = logging.getLogger(__name__)

client = OpenAI(api_key=settings.openai_key)


def generate_email(
    prompt: str,
    model: str | None = None,
    max_tokens: int | None = 2000,
    temperature: float | None = None,
) -> str:
    """Generate an email body using OpenAI's Responses API."""
    params = {
        "model": model or settings.openai_model,
        "input": prompt,
        "reasoning": {"effort": "low"},
    }
    if max_tokens is not None:
        params["max_output_tokens"] = max_tokens
    if temperature is not None:
        params["temperature"] = temperature
    logger.debug("OpenAI request params: %s", params)
    try:
        response = client.responses.create(**params)
    except OpenAIError as exc:
        raise OpenAIError(f"Failed to generate email: {exc}") from exc
    logger.debug("OpenAI raw response: %s", response)
    output_text = response.output_text or ""
    if response.status == "incomplete":
        if (
            response.incomplete_details
            and response.incomplete_details.reason == "max_output_tokens"
            and output_text.strip()
        ):
            logger.warning(
                "OpenAI response hit max_output_tokens; returning partial output"
            )
        else:
            raise OpenAIError(f"OpenAI response status {response.status}")
    elif response.status != "completed":
        raise OpenAIError(f"OpenAI response status {response.status}")
    if not output_text.strip():
        raise OpenAIError("OpenAI response contained no text output")
    return output_text
