"""Environment-driven settings."""

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

    cors_origins: list[str] = ["http://localhost:3000"]
    rate_limit: str = "120/minute"

    @property
    def provider_timeout_s(self) -> float:
        return self.web_provider_timeout_ms / 1000


settings = Settings()
