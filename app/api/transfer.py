from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.dependencies import get_current_user
from app.database import get_db
from app.models import User, Wallet
from app.schemas.transfer import (
    TransferConfirmRequest,
    TransferCreateRequest,
    TransferPreviewRequest,
    TransferPreviewResponse,
    TransferResponse,
)
from app.services.currency_service import get_exchange_rate
from app.services.transfer_preview_service import preview_transfer
from app.services.transfer_service import create_transfer


router = APIRouter(
    prefix="/api/v1/transfers",
    tags=["Transfers"],
)


@router.post("", response_model=TransferResponse)
async def create_transfer_request(
    payload: TransferCreateRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    raise HTTPException(
        status_code=400,
        detail="Use /preview then /confirm to create a transfer.",
    )


@router.post("/preview", response_model=TransferPreviewResponse)
async def preview(
    payload: TransferPreviewRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    try:
        result = await preview_transfer(
            db=db,
            sender=current_user,
            receiver_nexampay_id=payload.receiver_nexampay_id,
            amount=payload.amount,
        )
        return TransferPreviewResponse(**result)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc


@router.post("/confirm", response_model=TransferResponse)
async def confirm(
    payload: TransferConfirmRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    try:
        receiver_result = await db.execute(
            select(User)
            .where(
                User.nexampay_id == payload.receiver_nexampay_id,
                User.is_active.is_(True),
            )
            .limit(1)
        )
        receiver = receiver_result.scalar_one_or_none()
        if receiver is None:
            raise ValueError("Recipient not found.")

        sender_wallet_result = await db.execute(
            select(Wallet)
            .where(
                Wallet.user_id == current_user.id,
                Wallet.status == "active",
            )
            .limit(1)
        )
        sender_wallet = sender_wallet_result.scalar_one_or_none()

        receiver_wallet_result = await db.execute(
            select(Wallet)
            .where(
                Wallet.user_id == receiver.id,
                Wallet.status == "active",
            )
            .limit(1)
        )
        receiver_wallet = receiver_wallet_result.scalar_one_or_none()

        if sender_wallet is None or receiver_wallet is None:
            raise ValueError("Wallet not found.")

        exchange_rate = await get_exchange_rate(
            db,
            from_currency=sender_wallet.currency_code,
            to_currency=receiver_wallet.currency_code,
        )

        transfer = await create_transfer(
            db=db,
            sender=current_user,
            receiver_nexampay_id=payload.receiver_nexampay_id,
            amount=payload.amount,
            exchange_rate=exchange_rate,
            idempotency_key=payload.idempotency_key,
        )

        return TransferResponse(
            transfer_id=transfer.transfer_id,
            status=getattr(transfer.status, "value", transfer.status),
            receiver_nexampay_id=payload.receiver_nexampay_id,
            amount_sent=transfer.amount_sent,
            fee=transfer.fee,
            total_debited=transfer.total_debited,
            amount_received=transfer.amount_received,
            sender_currency=transfer.sender_currency,
            receiver_currency=transfer.receiver_currency,
            exchange_rate=transfer.exchange_rate,
        )
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
