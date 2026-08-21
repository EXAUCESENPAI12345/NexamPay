from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.dependencies import get_current_user
from app.database import get_db
from app.models import User
from app.schemas.history import (
    TransactionHistoryItem,
    TransactionHistoryResponse,
)
from app.services.history_service import (
    get_user_transactions,
)


router = APIRouter(
    prefix="/api/v1/history",
    tags=["History"],
)


@router.get(
    "/transactions",
    response_model=TransactionHistoryResponse,
)
async def transaction_history(
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
    transaction_status: str | None = Query(
        default=None,
    ),
    current_user: User = Depends(
        get_current_user
    ),
    db: AsyncSession = Depends(get_db),
):
    transactions, total = (
        await get_user_transactions(
            db=db,
            user=current_user,
            page=page,
            page_size=page_size,
            transaction_type=transaction_type,
            transaction_status=transaction_status,
        )
    )

    items = [
        TransactionHistoryItem(
            transaction_id=t.transaction_id,
            type=str(t.type),
            status=str(t.status),
            amount=t.amount,
            fee=t.fee,
            total_amount=t.total_amount,
            currency_code=t.currency_code,
            provider=t.provider,
            description=t.description,
            created_at=t.created_at.isoformat(),
            completed_at=(
                t.completed_at.isoformat()
                if t.completed_at
                else None
            ),
        )
        for t in transactions
    ]

    return TransactionHistoryResponse(
        items=items,
        page=page,
        page_size=page_size,
        total=total,
    )