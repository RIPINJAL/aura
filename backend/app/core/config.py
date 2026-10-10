from functools import lru_cache
from pathlib import Path

from pydantic import model_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    app_name: str = "AURA"
    app_env: str = "development"
    api_host: str = "0.0.0.0"
    api_port: int = 8000
    secret_key: str = "change-me-in-production"
    algorithm: str = "HS256"
    access_token_expire_minutes: int = 60
    database_url: str = "sqlite:///./aura.db"
    redis_url: str = "redis://localhost:6379/0"
    llm_base_url: str = ""
    llm_api_key: str = ""
    llm_model: str = ""
    llm_timeout_seconds: float = 30.0

    model_config = SettingsConfigDict(
        env_file=Path(__file__).resolve().parents[3] / ".env",
        extra="ignore",
    )

    @model_validator(mode="after")
    def validate_production_secret(self):
        if self.app_env.lower() in {"prod", "production"} and (
            self.secret_key == "change-me-in-production" or len(self.secret_key) < 32
        ):
            raise ValueError("Production requires a non-placeholder SECRET_KEY of at least 32 characters")
        return self


@lru_cache
def get_settings() -> Settings:
    return Settings()
