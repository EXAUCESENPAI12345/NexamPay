from decimal import Decimal
from datetime import datetime, timezone

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models import ExchangeRate


async def get_exchange_rate(
    db: AsyncSession,
    *,
    from_currency: str,
    to_currency: str,
) -> Decimal:

    if from_currency == to_currency:
        return Decimal("1")

    now = datetime.now(timezone.utc)

    result = await db.execute(
        select(ExchangeRate)
        .where(
            ExchangeRate.from_currency
            == from_currency,

            ExchangeRate.to_currency
            == to_currency,

            ExchangeRate.is_active.is_(True),

            ExchangeRate.valid_from <= now,

            (
                ExchangeRate.valid_until.is_(None)
                |
                (ExchangeRate.valid_until > now)
            ),
        )
        .order_by(
            ExchangeRate.valid_from.desc()
        )
        .limit(1)
    )

    exchange_rate = (
        result.scalar_one_or_none()
    )

    if exchange_rate is None:
        raise ValueError(
            "Exchange rate unavailable."
        )

    if exchange_rate.rate <= 0:
        raise ValueError(
            "Invalid exchange rate."
        )

    return exchange_rate.rate