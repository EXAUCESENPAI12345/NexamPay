from decimal import Decimal

from pydantic import BaseModel


class TransactionItem(BaseModel):
    transaction_id: str
    type: str
    status: str
    amount: Decimal
    fee: Decimal
    total_amount: Decimal
    currency_code: str
    description: str | None
    created_at: str


class TransactionListResponse(BaseModel):
    items: list[TransactionItem]
    page: int
    page_size: int
    total: int