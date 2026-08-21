from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.dependencies import get_current_user
from app.database import get_db
from app.models import User
from app.schemas.withdrawal import (
    WithdrawalCreateRequest,
    WithdrawalResponse,
)
from app.services.withdrawal_service import (
    create_withdrawal,
)


router = APIRouter(
    prefix="/api/v1/withdrawals",
    tags=["Withdrawals"],
)


@router.post(
    "",
    response_model=WithdrawalResponse,
)
async def create_withdrawal_request(
    payload: WithdrawalCreateRequest,
    current_user: User = Depends(
        get_current_user
    ),
    db: AsyncSession = Depends(get_db),
):
    try:
        withdrawal = await create_withdrawal(
            db=db,
            user=current_user,
            country_id=payload.country_id,
            network_id=payload.network_id,
            phone_number=payload.phone_number,
            amount=payload.amount,
        )

    except ValueError as exc:
        raise HTTPException(
            status_code=400,
            detail=str(exc),
        ) from exc

    return WithdrawalResponse(
        withdrawal_id=withdrawal.withdrawal_id,
        status=getattr(withdrawal.status, "value", withdrawal.status),
        amount=withdrawal.amount,
        fee=withdrawal.fee,
        total_debited=(
            withdrawal.total_debited
        ),
        currency_code=(
            withdrawal.currency_code
        ),
    )