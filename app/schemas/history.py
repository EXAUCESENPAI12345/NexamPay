from decimal import Decimal

from pydantic import BaseModel


class TransactionHistoryItem(BaseModel):
    transaction_id: str
    type: str
    status: str
    amount: Decimal
    fee: Decimal
    total_amount: Decimal
    currency_code: str
    provider: str | None
    description: str | None
    created_at: str
    completed_at: str | None


class TransactionHistoryResponse(BaseModel):
    items: list[TransactionHistoryItem]
    page: int
    page_size: int
    total: int