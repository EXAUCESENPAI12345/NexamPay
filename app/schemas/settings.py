from pydantic import BaseModel, Field


class SettingsResponse(BaseModel):
    language: str
    currency_code: str | None
    color: str
    theme: str
    bot_notifications_enabled: bool


class SettingsUpdateRequest(BaseModel):
    language: str | None = Field(default=None, pattern=r"^(fr|en)$")
    currency_code: str | None = Field(default=None, min_length=3, max_length=10)
    color: str | None = Field(default=None, pattern=r"^(nexam|green|white|black|pink)$")
    theme: str | None = Field(default=None, pattern=r"^(dark|light)$")
    bot_notifications_enabled: bool | None = None
