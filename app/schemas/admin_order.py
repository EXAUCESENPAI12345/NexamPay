from decimal import Decimal

from pydantic import BaseModel


class OrderAdminItem(BaseModel):
    order_number: str
    user_id: int
    status: str
    delivery_status: str
    total_amount: Decimal
    currency_code: str
    created_at: str


class OrderAdminListResponse(BaseModel):
    items: list[OrderAdminItem]
    page: int
    page_size: int
    total: int