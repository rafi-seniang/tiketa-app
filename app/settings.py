"""Typed settings. Every environment value the service reads is declared here, nowhere else."""

from functools import lru_cache
from typing import Literal

from pydantic import Field, SecretStr, model_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore", env_ignore_empty=True)

    environment: Literal["local", "test", "staging", "production"] = "local"
    log_level: str = "INFO"

    # Comma-separated keys accepted in the X-API-Key header. Empty disables auth (local only)
    api_keys: SecretStr = SecretStr("")
    # Signs guest session cookies and booking confirmations (HMAC-SHA256). Empty means a random one per process
    session_secret: SecretStr = SecretStr("")
    guest_session_days: int = Field(default=7, gt=0)
    # The parent domain the guest cookie is set for, so the chat agent on a sibling subdomain receives it too.
    # Empty keeps the cookie on this host only, which is right for localhost
    guest_cookie_domain: str = ""
    # Browser origins allowed to call the API (the web app in development and preview)
    cors_origins: list[str] = ["http://localhost:5174", "http://localhost:4174"]

    # SQLAlchemy URL of the cinema database. postgresql+psycopg://... for real use,
    # sqlite+aiosqlite:///./tiketa.db for a quick local run
    database_url: SecretStr

    cinema_name: str = "Tiketa Cinema"
    # Showtimes are stored in UTC and shown, and understood, in this timezone. A week runs Monday to Sunday in it
    cinema_timezone: str = "Asia/Jakarta"
    max_seats_per_booking: int = Field(default=8, gt=0)
    # How long a prepared booking may wait for its confirmation
    booking_confirmation_minutes: int = Field(default=10, gt=0)

    # Redis for the shared rate limit. Empty counts per process: local only
    redis_url: SecretStr = SecretStr("")
    redis_timeout_seconds: float = Field(default=2, gt=0)
    # Requests per caller (API key, guest, or client address without either) per minute on /v1
    rate_limit_per_minute: int = Field(default=60, gt=0)

    @model_validator(mode="after")
    def production_needs_secrets(self) -> "Settings":
        if self.environment == "production" and not (
            self.api_keys.get_secret_value() and self.session_secret.get_secret_value()
        ):
            raise ValueError("production needs API_KEYS and SESSION_SECRET")
        return self

    @property
    def api_key_list(self) -> list[str]:
        return [key.strip() for key in self.api_keys.get_secret_value().split(",") if key.strip()]


@lru_cache
def get_settings() -> Settings:
    return Settings()  # database_url comes from the environment
