from decimal import Decimal

from pydantic import BaseModel


class CategoryResponse(BaseModel):
    id: int
    name: str
    description: str | None


class ProductResponse(BaseModel):
    id: int
    category_id: int
    name: str
    description: str | None
    image_url: str
    price: Decimal
    currency_code: str
    stock: int
    is_active: bool


class ProductListResponse(BaseModel):
    items: list[ProductResponse]
    page: int
    page_size: int
    total: int