import secrets
from decimal import Decimal

from sqlalchemy.ext.asyncio import AsyncSession

from app.models import (
    RevenueLedger,
    RevenueStatus,
    RevenueType,
)


def generate_revenue_id() -> str:
    return "REV-" + secrets.token_hex(8).upper()


async def record_revenue(
    db: AsyncSession,
    *,
    revenue_type: RevenueType,
    amount: Decimal,
    currency_code: str,
    source_transaction_id: int | None = None,
    source_order_id: int | None = None,
    description: str | None = None,
) -> RevenueLedger:

    if amount <= 0:
        raise ValueError(
            "Revenue amount must be greater than zero."
        )

    revenue = RevenueLedger(
        revenue_id=generate_revenue_id(),
        revenue_type=revenue_type,
        status=RevenueStatus.COMPLETED,
        amount=amount,
        currency_code=currency_code,
        source_transaction_id=source_transaction_id,
        source_order_id=source_order_id,
        description=description,
    )

    db.add(revenue)

    await db.flush()

    return revenue