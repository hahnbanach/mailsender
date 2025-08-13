import openai

from ..config.settings import settings

openai.api_key = settings.openai_key


def generate_email(prompt: str) -> str:
    """Generate an email using OpenAI's completion API."""
    response = openai.Completion.create(model="gpt-3.5-turbo-instruct", prompt=prompt, max_tokens=500)
    return response["choices"][0]["text"]
