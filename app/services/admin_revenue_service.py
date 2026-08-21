from decimal import Decimal

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models import RevenueLedger


async def get_revenue_report(
    db: AsyncSession,
    *,
    page: int,
    page_size: int,
    revenue_type: str | None = None,
    currency_code: str | None = None,
):
    conditions = []

    if revenue_type:
        conditions.append(
            RevenueLedger.revenue_type == revenue_type
        )

    if currency_code:
        conditions.append(
            RevenueLedger.currency_code
            == currency_code
        )

    total_result = await db.execute(
        select(func.count(RevenueLedger.id))
        .where(*conditions)
    )

    total = total_result.scalar_one()

    offset = (page - 1) * page_size

    result = await db.execute(
        select(RevenueLedger)
        .where(*conditions)
        .order_by(
            RevenueLedger.created_at.desc()
        )
        .offset(offset)
        .limit(page_size)
    )

    items = list(result.scalars().all())

    summary_result = await db.execute(
        select(
            RevenueLedger.currency_code,
            func.coalesce(
                func.sum(RevenueLedger.amount),
                0,
            ),
        )
        .where(*conditions)
        .group_by(
            RevenueLedger.currency_code
        )
        .order_by(
            RevenueLedger.currency_code.asc()
        )
    )

    summaries = [
        {
            "currency_code": currency,
            "total_revenue": Decimal(total),
        }
        for currency, total in summary_result.all()
    ]

    return items, summaries, total