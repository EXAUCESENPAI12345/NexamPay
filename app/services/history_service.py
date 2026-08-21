from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models import Transaction, User


async def get_user_transactions(
    db: AsyncSession,
    user: User,
    page: int,
    page_size: int,
    transaction_type: str | None = None,
    transaction_status: str | None = None,
):
    offset = (page - 1) * page_size

    conditions = [
        Transaction.user_id == user.id
    ]

    if transaction_type:
        conditions.append(
            Transaction.type == transaction_type
        )

    if transaction_status:
        conditions.append(
            Transaction.status == transaction_status
        )

    total_result = await db.execute(
        select(func.count(Transaction.id))
        .where(*conditions)
    )

    total = total_result.scalar_one()

    result = await db.execute(
        select(Transaction)
        .where(*conditions)
        .order_by(
            Transaction.created_at.desc()
        )
        .offset(offset)
        .limit(page_size)
    )

    transactions = list(
        result.scalars().all()
    )

    return transactions, total