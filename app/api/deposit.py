from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.dependencies import get_current_user
from app.database import get_db
from app.models import User
from app.schemas.deposit import (
    DepositCreateRequest,
    DepositResponse,
)
from app.services.deposit_service import (
    create_deposit,
)


router = APIRouter(
    prefix="/api/v1/deposits",
    tags=["Deposits"],
)


@router.post(
    "",
    response_model=DepositResponse,
)
async def create_deposit_request(
    payload: DepositCreateRequest,
    current_user: User = Depends(
        get_current_user
    ),
    db: AsyncSession = Depends(get_db),
):
    try:
        deposit = await create_deposit(
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

    return DepositResponse(
        deposit_id=deposit.deposit_id,
        status=getattr(deposit.status, "value", deposit.status),
        amount=deposit.amount,
        fee=deposit.fee,
        total_amount=deposit.total_amount,
        currency_code=deposit.currency_code,
    )