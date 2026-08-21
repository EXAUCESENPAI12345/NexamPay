from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models import Product, ProductCategory


async def get_categories(
    db: AsyncSession,
) -> list[ProductCategory]:

    result = await db.execute(
        select(ProductCategory)
        .where(
            ProductCategory.is_active.is_(True)
        )
        .order_by(
            ProductCategory.name.asc()
        )
    )

    return list(result.scalars().all())


async def get_products(
    db: AsyncSession,
    *,
    page: int,
    page_size: int,
    category_id: int | None = None,
):

    conditions = [
        Product.is_active.is_(True)
    ]

    if category_id is not None:
        conditions.append(
            Product.category_id == category_id
        )

    total_result = await db.execute(
        select(func.count(Product.id))
        .where(*conditions)
    )

    total = total_result.scalar_one()

    offset = (page - 1) * page_size

    result = await db.execute(
        select(Product)
        .where(*conditions)
        .order_by(
            Product.created_at.desc()
        )
        .offset(offset)
        .limit(page_size)
    )

    products = list(
        result.scalars().all()
    )

    return products, total