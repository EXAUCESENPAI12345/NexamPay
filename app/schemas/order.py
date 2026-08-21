from decimal import Decimal

from pydantic import BaseModel, Field


class CreateOrderRequest(BaseModel):
    product_id: int = Field(gt=0)
    quantity: int = Field(gt=0, le=100)
    idempotency_key: str = Field(
        min_length=16,
        max_length=100,
    )


class OrderResponse(BaseModel):
    order_number: str
    status: str
    delivery_status: str
    product_name: str
    quantity: int
    total_amount: Decimal
    currency_code: str