from fastapi import (
    APIRouter,
    Depends,
    Query,
)
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.dependencies import get_current_user
from app.database import get_db
from app.models import Transaction, User
from app.schemas.transaction import (
    TransactionItem,
    TransactionListResponse,
)


router = APIRouter(
    prefix="/api/v1/transactions",
    tags=["Transactions"],
)


@router.get(
    "",
    response_model=TransactionListResponse,
)
async def get_transactions(
    page: int = Query(
        default=1,
        ge=1,
    ),
    page_size: int = Query(
        default=20,
        ge=1,
        le=100,
    ),
    transaction_type: str | None = Query(
        default=None,
    ),
    status: str | None = Query(
        default=None,
    ),
    current_user: User = Depends(
        get_current_user
    ),
    db: AsyncSession = Depends(get_db),
):
    conditions = [
        Transaction.user_id
        == current_user.id
    ]

    if transaction_type:
        conditions.append(
            Transaction.type
            == transaction_type
        )

    if status:
        conditions.append(
            Transaction.status
            == status
        )

    total_result = await db.execute(
        select(
            func.count(Transaction.id)
        )
        .where(*conditions)
    )

    total = total_result.scalar_one()

    offset = (
        page - 1
    ) * page_size

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

    return TransactionListResponse(
        items=[
            TransactionItem(
                transaction_id=(
                    item.transaction_id
                ),
                type=item.type,
                status=item.status,
                amount=item.amount,
                fee=item.fee,
                total_amount=(
                    item.total_amount
                ),
                currency_code=(
                    item.currency_code
                ),
                description=(
                    item.description
                ),
                created_at=(
                    item.created_at.isoformat()
                ),
            )
            for item in transactions
        ],
        page=page,
        page_size=page_size,
        total=total,
    )