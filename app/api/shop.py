from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.schemas.product import (
    CategoryResponse,
    ProductListResponse,
    ProductResponse,
)
from app.services.shop_service import (
    get_categories,
    get_products,
)


router = APIRouter(
    prefix="/api/v1/shop",
    tags=["Shop"],
)


@router.get(
    "/categories",
    response_model=list[CategoryResponse],
)
async def categories(
    db: AsyncSession = Depends(get_db),
):
    categories = await get_categories(db)

    return [
        CategoryResponse(
            id=category.id,
            name=category.name,
            description=category.description,
        )
        for category in categories
    ]


@router.get(
    "/products",
    response_model=ProductListResponse,
)
async def products(
    page: int = Query(
        default=1,
        ge=1,
    ),
    page_size: int = Query(
        default=20,
        ge=1,
        le=100,
    ),
    category_id: int | None = Query(
        default=None,
        gt=0,
    ),
    db: AsyncSession = Depends(get_db),
):
    products, total = await get_products(
        db=db,
        page=page,
        page_size=page_size,
        category_id=category_id,
    )

    return ProductListResponse(
        items=[
            ProductResponse(
                id=product.id,
                category_id=product.category_id,
                name=product.name,
                description=product.description,
                image_url=product.image_url,
                price=product.price,
                currency_code=product.currency_code,
                stock=product.stock,
                is_active=product.is_active,
            )
            for product in products
        ],
        page=page,
        page_size=page_size,
        total=total,
    )