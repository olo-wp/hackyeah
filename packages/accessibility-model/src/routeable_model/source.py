"""Where a piece of information came from."""

from enum import StrEnum

from pydantic import BaseModel, Field


class SourceType(StrEnum):
    OPENSTREETMAP = "openstreetmap"
    CITY_OPEN_DATA = "city_open_data"
    OFFICIAL_WEBSITE = "official_website"
    USER_REPORT = "user_report"
    PARTNER_API = "partner_api"
    DEMO_DATA = "demo_data"


class DataSource(BaseModel):
    id: str
    type: SourceType
    name: str
    url: str | None = None
    license: str | None = Field(default=None, description="Terms the data may be reused under")
