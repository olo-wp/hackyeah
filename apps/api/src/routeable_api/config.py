"""Environment-driven settings."""

from pydantic import Field, SecretStr
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    api_port: int = 3001
    database_url: str | None = None

    nominatim_url: str = "https://nominatim.openstreetmap.org"
    osm_overpass_url: str = "https://overpass-api.de/api/interpreter"
    user_agent: str = "RouteAble/0.1 (hackyeah-2026)"

    web_provider_timeout_ms: int = 5000
    provider_cache_ttl_hours: int = 24
    stale_after_days: int = 180
    gemini_api_key: SecretStr | None = None
    gemini_model: str = "gemini-3.5-flash-lite"
    gemini_fallback_model: str | None = "gemini-3.5-flash-lite"
    gemini_timeout_s: float = Field(default=60.0, gt=0)
    gemini_max_input_chars: int = Field(default=60000, gt=0)

    cors_origins: list[str] = ["http://localhost:3000"]
    rate_limit: str = "120/minute"

    @property
    def provider_timeout_s(self) -> float:
        return self.web_provider_timeout_ms / 1000


settings = Settings()
