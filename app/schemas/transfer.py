from decimal import Decimal

from pydantic import BaseModel, Field


class TransferCreateRequest(BaseModel):
    receiver_nexampay_id: str = Field(
        min_length=12,
        max_length=12,
    )
    amount: Decimal = Field(
        gt=0,
        max_digits=20,
        decimal_places=2,
    )


class TransferPreviewRequest(BaseModel):
    receiver_nexampay_id: str = Field(
        min_length=12,
        max_length=12,
    )
    amount: Decimal = Field(
        gt=0,
        max_digits=20,
        decimal_places=2,
    )


class TransferPreviewResponse(BaseModel):
    receiver_nexampay_id: str
    amount_sent: Decimal
    fee: Decimal
    total_debited: Decimal
    amount_received: Decimal
    sender_currency: str
    receiver_currency: str
    exchange_rate: Decimal


class TransferConfirmRequest(BaseModel):
    receiver_nexampay_id: str = Field(
        min_length=12,
        max_length=12,
    )
    amount: Decimal = Field(
        gt=0,
        max_digits=20,
        decimal_places=2,
    )
    idempotency_key: str = Field(
        min_length=16,
        max_length=100,
    )


class TransferResponse(BaseModel):
    transfer_id: str
    status: str
    receiver_nexampay_id: str
    amount_sent: Decimal
    fee: Decimal
    total_debited: Decimal
    amount_received: Decimal
    sender_currency: str
    receiver_currency: str
    exchange_rate: Decimal
