from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models import Product, ProductCategory


async def create_category(
    db: AsyncSession,
    *,
    name: str,
    description: str | None,
):
    existing = await db.execute(
        select(ProductCategory)
        .where(
            ProductCategory.name == name
        )
        .limit(1)
    )

    if existing.scalar_one_or_none():
        raise ValueError(
            "Category already exists."
        )

    category = ProductCategory(
        name=name,
        description=description,
        is_active=True,
    )

    db.add(category)

    await db.commit()
    await db.refresh(category)

    return category


async def create_product(
    db: AsyncSession,
    *,
    category_id: int,
    name: str,
    description: str | None,
    image_url: str,
    price,
    currency_code: str,
    stock: int,
):
    category_result = await db.execute(
        select(ProductCategory)
        .where(
            ProductCategory.id == category_id,
            ProductCategory.is_active.is_(True),
        )
        .limit(1)
    )

    category = (
        category_result.scalar_one_or_none()
    )

    if category is None:
        raise ValueError(
            "Category not found."
        )

    product = Product(
        category_id=category_id,
        name=name,
        description=description,
        image_url=image_url,
        price=price,
        currency_code=currency_code,
        stock=stock,
        is_active=True,
    )

    db.add(product)

    await db.commit()
    await db.refresh(product)

    return product


async def update_product(
    db: AsyncSession,
    *,
    product_id: int,
    data: dict,
):
    result = await db.execute(
        select(Product)
        .where(
            Product.id == product_id
        )
        .with_for_update()
    )

    product = result.scalar_one_or_none()

    if product is None:
        raise ValueError(
            "Product not found."
        )

    if "category_id" in data:
        category_result = await db.execute(
            select(ProductCategory)
            .where(
                ProductCategory.id
                == data["category_id"],
                ProductCategory.is_active.is_(True),
            )
            .limit(1)
        )

        if (
            category_result
            .scalar_one_or_none()
            is None
        ):
            raise ValueError(
                "Category not found."
            )

    for field, value in data.items():
        setattr(product, field, value)

    await db.commit()
    await db.refresh(product)

    return product