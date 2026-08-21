from datetime import datetime
from pydantic import BaseModel, Field


class CardApplicationCreateRequest(BaseModel):
    country_id: int = Field(gt=0)
    cardholder_name: str = Field(min_length=2, max_length=255)
    phone_number: str = Field(min_length=6, max_length=30)


class CardApplicationResponse(BaseModel):
    application_id: str
    status: str
    cardholder_name: str
    phone_number: str
    currency_code: str
    admin_note: str | None = None
    rejection_reason: str | None = None
    reviewed_at: datetime | None = None


class VirtualCardResponse(BaseModel):
    card_id: str
    status: str
    currency_code: str
    brand: str | None = None
    masked_number: str | None = None
    last4: str | None = None
    expiry_month: int | None = None
    expiry_year: int | None = None


class CardApprovalRequest(BaseModel):
    admin_note: str | None = Field(default=None, max_length=1000)
    brand: str | None = Field(default=None, max_length=30)
    masked_number: str | None = Field(default=None, max_length=32)
    last4: str | None = Field(default=None, min_length=4, max_length=4)
    expiry_month: int | None = Field(default=None, ge=1, le=12)
    expiry_year: int | None = Field(default=None, ge=2026, le=2100)
    provider_card_id: str | None = Field(default=None, max_length=255)


class CardRejectionRequest(BaseModel):
    reason: str = Field(min_length=1, max_length=1000)


class CardApplicationAdminItem(BaseModel):
    application_id: str
    user_id: int
    nexampay_id: str
    telegram_id: int
    cardholder_name: str
    phone_number: str
    country_code: str
    country_name: str
    currency_code: str
    status: str
    created_at: datetime
    reviewed_at: datetime | None = None
    admin_note: str | None = None
    rejection_reason: str | None = None
