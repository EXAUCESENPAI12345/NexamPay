from decimal import Decimal

from pydantic import BaseModel


class RevenueItem(BaseModel):
    revenue_id: str
    revenue_type: str
    status: str
    amount: Decimal
    currency_code: str
    source_transaction_id: int | None
    source_order_id: int | None
    description: str | None
    created_at: str


class RevenueSummary(BaseModel):
    currency_code: str
    total_revenue: Decimal


class RevenueListResponse(BaseModel):
    items: list[RevenueItem]
    summaries: list[RevenueSummary]
    page: int
    page_size: int
    total: int