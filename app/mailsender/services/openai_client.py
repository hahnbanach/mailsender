from openai import OpenAI
from openai.error import OpenAIError

from ..config.settings import settings

client = OpenAI(api_key=settings.openai_key)


def generate_email(
    prompt: str,
    model: str | None = None,
    temperature: float = 0.7,
    max_tokens: int = 500,
) -> str:
    """Generate an email using OpenAI's Responses API.

    Parameters can override the defaults from ``settings.ini``.
    """
    try:
        response = client.responses.create(
            model=model or settings.openai_model,
            input=prompt,
            temperature=temperature,
            max_output_tokens=max_tokens,
        )
    except OpenAIError as exc:
        raise OpenAIError(f"Failed to generate email: {exc}") from exc
    return response.output[0].content[0].text
