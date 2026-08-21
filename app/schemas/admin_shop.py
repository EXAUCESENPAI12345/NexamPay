from decimal import Decimal

from pydantic import BaseModel, Field


class CategoryCreateRequest(BaseModel):
    name: str = Field(min_length=2, max_length=100)
    description: str | None = Field(
        default=None,
        max_length=1000,
    )


class ProductCreateRequest(BaseModel):
    category_id: int = Field(gt=0)

    name: str = Field(
        min_length=2,
        max_length=255,
    )

    description: str | None = Field(
        default=None,
        max_length=5000,
    )

    image_url: str = Field(
        min_length=1,
        max_length=1000,
    )

    price: Decimal = Field(
        gt=0,
        max_digits=20,
        decimal_places=2,
    )

    currency_code: str = Field(
        min_length=3,
        max_length=10,
    )

    stock: int = Field(
        ge=0,
    )


class ProductUpdateRequest(BaseModel):
    category_id: int | None = Field(
        default=None,
        gt=0,
    )

    name: str | None = Field(
        default=None,
        min_length=2,
        max_length=255,
    )

    description: str | None = Field(
        default=None,
        max_length=5000,
    )

    image_url: str | None = Field(
        default=None,
        min_length=1,
        max_length=1000,
    )

    price: Decimal | None = Field(
        default=None,
        gt=0,
        max_digits=20,
        decimal_places=2,
    )

    currency_code: str | None = Field(
        default=None,
        min_length=3,
        max_length=10,
    )

    stock: int | None = Field(
        default=None,
        ge=0,
    )

    is_active: bool | None = None