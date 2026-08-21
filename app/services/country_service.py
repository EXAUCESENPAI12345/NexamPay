from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models import Country, MobileMoneyNetwork


async def get_active_countries(
    db: AsyncSession,
) -> list[Country]:
    result = await db.execute(
        select(Country)
        .where(Country.is_active.is_(True))
        .order_by(Country.name.asc())
    )

    return list(result.scalars().all())


async def get_country_networks(
    db: AsyncSession,
    country_id: int,
) -> list[MobileMoneyNetwork]:
    result = await db.execute(
        select(MobileMoneyNetwork)
        .where(
            MobileMoneyNetwork.country_id == country_id,
            MobileMoneyNetwork.is_active.is_(True),
        )
        .order_by(MobileMoneyNetwork.name.asc())
    )

    return list(result.scalars().all())