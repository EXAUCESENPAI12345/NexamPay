from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models import Country, MobileMoneyNetwork


async def validate_payment_destination(
    db: AsyncSession,
    country_id: int,
    network_id: int,
) -> tuple[Country, MobileMoneyNetwork]:

    country_result = await db.execute(
        select(Country)
        .where(
            Country.id == country_id,
            Country.is_active.is_(True),
        )
    )

    country = country_result.scalar_one_or_none()

    if country is None:
        raise ValueError(
            "Selected country is unavailable."
        )

    network_result = await db.execute(
        select(MobileMoneyNetwork)
        .where(
            MobileMoneyNetwork.id == network_id,
            MobileMoneyNetwork.country_id == country.id,
            MobileMoneyNetwork.is_active.is_(True),
        )
    )

    network = network_result.scalar_one_or_none()

    if network is None:
        raise ValueError(
            "Selected Mobile Money network is unavailable "
            "for this country."
        )

    return country, network