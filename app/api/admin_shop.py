from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.admin_dependencies import (
    get_current_admin,
)
from app.database import get_db
from app.models import User, Product, ProductCategory
from app.schemas.admin_shop import (
    CategoryCreateRequest,
    ProductCreateRequest,
    ProductUpdateRequest,
)
from app.services.admin_shop_service import (
    create_category,
    create_product,
    update_product,
)


router = APIRouter(
    prefix="/api/v1/admin/shop",
    tags=["Admin Shop"],
)



@router.get("/categories")
async def admin_categories(
    current_admin: User = Depends(get_current_admin),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(
        select(ProductCategory)
        .order_by(ProductCategory.name.asc())
    )
    return {
        "items": [
            {
                "id": item.id,
                "name": item.name,
                "description": item.description,
                "is_active": item.is_active,
            }
            for item in result.scalars().all()
        ]
    }


@router.get("/products")
async def admin_products(
    active_only: bool = Query(default=False),
    current_admin: User = Depends(get_current_admin),
    db: AsyncSession = Depends(get_db),
):
    query = select(Product).order_by(Product.created_at.desc())
    if active_only:
        query = query.where(Product.is_active.is_(True))
    result = await db.execute(query)
    return {
        "items": [
            {
                "id": item.id,
                "category_id": item.category_id,
                "name": item.name,
                "description": item.description,
                "image_url": item.image_url,
                "price": item.price,
                "currency_code": item.currency_code,
                "stock": item.stock,
                "is_active": item.is_active,
            }
            for item in result.scalars().all()
        ]
    }

@router.post("/categories")
async def add_category(
    payload: CategoryCreateRequest,
    current_admin: User = Depends(
        get_current_admin
    ),
    db: AsyncSession = Depends(get_db),
):
    try:
        category = await create_category(
            db,
            name=payload.name,
            description=payload.description,
        )

        return {
            "success": True,
            "id": category.id,
            "name": category.name,
        }

    except ValueError as exc:
        raise HTTPException(
            status_code=400,
            detail=str(exc),
        ) from exc


@router.post("/products")
async def add_product(
    payload: ProductCreateRequest,
    current_admin: User = Depends(
        get_current_admin
    ),
    db: AsyncSession = Depends(get_db),
):
    try:
        product = await create_product(
            db,
            category_id=payload.category_id,
            name=payload.name,
            description=payload.description,
            image_url=payload.image_url,
            price=payload.price,
            currency_code=payload.currency_code,
            stock=payload.stock,
        )

        return {
            "success": True,
            "id": product.id,
            "name": product.name,
        }

    except ValueError as exc:
        raise HTTPException(
            status_code=400,
            detail=str(exc),
        ) from exc


@router.patch("/products/{product_id}")
async def edit_product(
    product_id: int,
    payload: ProductUpdateRequest,
    current_admin: User = Depends(
        get_current_admin
    ),
    db: AsyncSession = Depends(get_db),
):
    try:
        product = await update_product(
            db,
            product_id=product_id,
            data=payload.model_dump(
                exclude_unset=True
            ),
        )

        return {
            "success": True,
            "id": product.id,
            "name": product.name,
            "stock": product.stock,
            "is_active": product.is_active,
        }

    except ValueError as exc:
        raise HTTPException(
            status_code=400,
            detail=str(exc),
        ) from exc