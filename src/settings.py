from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    anthropic_api_key: str
    anthropic_model: str = "claude-sonnet-4-20250514"
    database_url: str = "sqlite+aiosqlite:///db.sqlite"
    max_concurrency: int = 20

    class Config:
        env_file = ".env"


settings = Settings()
