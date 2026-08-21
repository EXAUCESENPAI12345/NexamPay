from decimal import Decimal

from pydantic import BaseModel


class WalletResponse(BaseModel):
    balance: Decimal
    currency_code: str
    status: str


class ProfileResponse(BaseModel):
    nexampay_id: str
    telegram_username: str | None
    first_name: str | None
    last_name: str | None
    photo_url: str | None
    country_code: str
    country_name: str
    currency_code: str
    network_id: int | None = None
    network_code: str | None = None
    network_name: str | None = None
    wallet: WalletResponse