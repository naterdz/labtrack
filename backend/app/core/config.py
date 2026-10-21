from pathlib import Path
from typing import Literal

from pydantic import Field, SecretStr, model_validator
from pydantic_settings import BaseSettings, SettingsConfigDict

ROOT = Path(__file__).resolve().parents[3]


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=ROOT / ".env", extra="ignore")

    app_env: Literal["development", "test", "production"] = "development"
    database_url: str = "sqlite:///./labtrack.db"
    secret_key: SecretStr = Field(min_length=32)
    cookie_secure: bool = False
    session_ttl_seconds: int = Field(default=28800, ge=60, le=604800)

    @model_validator(mode="after")
    def production_requires_secure_cookies(self):
        if self.app_env == "production" and not self.cookie_secure:
            raise ValueError("COOKIE_SECURE debe ser true en producción")
        return self
