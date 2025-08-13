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
        "`{other_info}`. The body must be HTML and include an `<img>` tag "
        "referencing `{pixel_url}` as the tracking pixel."
    )
    db_host: str = "localhost"
    db_port: int = 5432
    db_user: str = "user"
    db_password: str = "password"
    db_name: str = "mailsender"

    class Config:
        env_file = ".env"

    @property
    def database_url(self) -> str:
        return (
            f"postgresql://{self.db_user}:{self.db_password}@{self.db_host}:{self.db_port}/{self.db_name}"
        )

settings = Settings()
