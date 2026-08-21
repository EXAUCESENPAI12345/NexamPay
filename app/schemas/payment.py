from decimal import Decimal

from pydantic import BaseModel, Field


class DepositRequest(BaseModel):
    country_id: int = Field(gt=0)
    network_id: int = Field(gt=0)

    mobile_number: str = Field(
        min_length=6,
        max_length=30,
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


class WithdrawalRequest(BaseModel):
    country_id: int = Field(gt=0)
    network_id: int = Field(gt=0)

    mobile_number: str = Field(
        min_length=6,
        max_length=30,
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


class PaymentOperationResponse(BaseModel):
    transaction_id: str
    status: str
    amount: Decimal
    fee: Decimal
    total_amount: Decimal
    currency_code: str
    provider: str