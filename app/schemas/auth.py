from pydantic import BaseModel, Field


class TelegramAuthRequest(BaseModel):
    init_data: str = Field(min_length=1, max_length=5000)


class CreateAccountRequest(TelegramAuthRequest):
    country_id: int = Field(gt=0)
    network_id: int | None = Field(default=None, gt=0)
    pin: str = Field(min_length=4, max_length=4, pattern=r"^\d{4}$")


class SelectCountryRequest(BaseModel):
    country_id: int = Field(gt=0)


class AuthResponse(BaseModel):
    is_new_user: bool
    requires_country: bool
    session_token: str | None
    nexampay_id: str | None
    telegram_id: int
