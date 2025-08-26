from pydantic import BaseSettings


class Settings(BaseSettings):
    openai_key: str = "sk-dummy"
    sendgrid_key: str = "sendgrid-dummy"
    mrcall_user: str = "mrcall_user"
    mrcall_password: str = "mrcall_password"
    mrcall_business_id: str = "mrcall_business"
    email_prompt: str = (
        "Generate a JSON object with fields `recipient`, `subject`, and `body` "
        "for the recipient `{email_address}` using additional lead details "
        "`{custom_args}`. The body must be HTML."
    )
    database_url: str = "sqlite:///./mailsender.db"

    class Config:
        env_file = ".env"

settings = Settings()
