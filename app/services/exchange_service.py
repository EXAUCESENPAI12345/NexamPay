from decimal import Decimal

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models import ExchangeRate


async def get_exchange_rate(
    db: AsyncSession,
    base_currency: str,
    quote_currency: str,
) -> Decimal:

    if base_currency == quote_currency:
        return Decimal("1")

    result = await db.execute(
        select(ExchangeRate)
        .where(
            ExchangeRate.base_currency == base_currency,
            ExchangeRate.quote_currency == quote_currency,
            ExchangeRate.is_active.is_(True),
        )
        .limit(1)
    )

    exchange_rate = result.scalar_one_or_none()

    if exchange_rate is None:
        raise ValueError(
            "Exchange rate is currently unavailable."
        )

    return exchange_rate.rate