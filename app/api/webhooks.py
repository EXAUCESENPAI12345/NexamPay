from fastapi import APIRouter, Depends, Header, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.schemas.webhook import (
    DepositWebhookRequest,
    WithdrawalWebhookRequest,
)
from app.services.deposit_confirmation_service import confirm_deposit
from app.services.withdrawal_confirmation_service import process_withdrawal_result


router = APIRouter(
    prefix="/api/v1/webhooks",
    tags=["Webhooks"],
)


async def _require_provider_signature(
    signature: str | None,
) -> None:
    if not signature:
        raise HTTPException(
            status_code=401,
            detail="Missing provider signature.",
        )


@router.post("/deposits")
async def deposit_webhook(
    payload: DepositWebhookRequest,
    x_provider_signature: str | None = Header(default=None),
    db: AsyncSession = Depends(get_db),
):
    await _require_provider_signature(x_provider_signature)

    try:
        deposit = await confirm_deposit(
            db,
            provider_transaction_id=payload.provider_transaction_id,
            provider_status=payload.status,
        )
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc

    return {
        "success": True,
        "deposit_id": deposit.deposit_id,
        "status": deposit.status,
    }


@router.post("/withdrawals")
async def withdrawal_webhook(
    payload: WithdrawalWebhookRequest,
    x_provider_signature: str | None = Header(default=None),
    db: AsyncSession = Depends(get_db),
):
    await _require_provider_signature(x_provider_signature)

    try:
        withdrawal = await process_withdrawal_result(
            db,
            provider_transaction_id=payload.provider_transaction_id,
            provider_status=payload.status,
        )
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc

    return {
        "success": True,
        "withdrawal_id": withdrawal.withdrawal_id,
        "status": withdrawal.status,
    }
