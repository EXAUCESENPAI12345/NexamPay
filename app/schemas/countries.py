from pydantic import BaseModel, ConfigDict


class CountryResponse(BaseModel):
    id: int
    code: str
    name: str
    currency_code: str
    currency_name: str
    flag_emoji: str

    model_config = ConfigDict(from_attributes=True)


class MobileMoneyNetworkResponse(BaseModel):
    id: int
    name: str
    code: str
    logo_url: str | None

    model_config = ConfigDict(from_attributes=True)