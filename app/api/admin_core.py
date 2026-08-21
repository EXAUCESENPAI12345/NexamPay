from fastapi import APIRouter, Depends, HTTPException, Query
import hmac
from pydantic import BaseModel, Field
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.admin_dependencies import get_current_admin
from app.database import get_db
from app.models import User
from app.config import settings
from app.services.telegram_auth_service import validate_telegram_init_data
from app.services.admin_core_service import (
    get_admin_stats,
    list_pending_deposits,
    list_pending_withdrawals,
    list_transfers,
    approve_deposit,
    reject_deposit,
    approve_withdrawal,
    reject_withdrawal,
)

router = APIRouter(prefix="/api/v1/admin", tags=["Admin"])


def _item(x):
    return {
        "id": getattr(x, "id", None),
        "reference": getattr(x, "deposit_id", None)
        or getattr(x, "withdrawal_id", None)
        or getattr(x, "transfer_id", None),
        "user_id": getattr(x, "user_id", None)
        or getattr(x, "sender_id", None),
        "amount": getattr(x, "amount", None)
        or getattr(x, "amount_sent", None),
        "fee": getattr(x, "fee", None),
        "total_amount": getattr(x, "total_amount", None)
        or getattr(x, "total_debited", None),
        "currency": getattr(x, "currency_code", None)
        or getattr(x, "sender_currency", None),
        "status": getattr(getattr(x, "status", None), "value", getattr(x, "status", None)),
        "created_at": x.created_at.isoformat() if getattr(x, "created_at", None) else None,
    }



class AdminAuthRequest(BaseModel):
    code: str = Field(min_length=1, max_length=128)
    telegram_init_data: str = Field(min_length=1, max_length=5000)


@router.post("/auth")
async def admin_auth(payload: AdminAuthRequest):
    if settings.admin_telegram_id is None or not settings.admin_access_code:
        raise HTTPException(status_code=503, detail="Admin access is not configured.")
    try:
        telegram_user = validate_telegram_init_data(payload.telegram_init_data)
        telegram_id = int(telegram_user["id"])
    except (ValueError, TypeError) as exc:
        raise HTTPException(status_code=401, detail="Invalid Telegram authentication.") from exc

    if telegram_id != settings.admin_telegram_id:
        raise HTTPException(status_code=403, detail="Administrator access required.")

    if not hmac.compare_digest(payload.code, settings.admin_access_code):
        raise HTTPException(status_code=403, detail="Invalid administrator code.")

    return {"authorized": True}

@router.get("/session")
async def admin_session(current_admin: User = Depends(get_current_admin)):
    return {
        "authorized": True,
        "telegram_id": current_admin.telegram_id,
        "nexampay_id": current_admin.nexampay_id,
    }


@router.get("/stats")
async def admin_stats(
    current_admin: User = Depends(get_current_admin),
    db: AsyncSession = Depends(get_db),
):
    return await get_admin_stats(db)


@router.get("/deposits")
async def admin_deposits(
    limit: int = Query(default=100, ge=1, le=200),
    current_admin: User = Depends(get_current_admin),
    db: AsyncSession = Depends(get_db),
):
    items = await list_pending_deposits(db, limit)
    return {"items": [_item(x) for x in items]}


@router.post("/deposits/{deposit_id}/approve")
async def admin_deposit_approve(
    deposit_id: str,
    current_admin: User = Depends(get_current_admin),
    db: AsyncSession = Depends(get_db),
):
    try:
        item = await approve_deposit(
            db, deposit_id=deposit_id,
            admin_telegram_id=current_admin.telegram_id,
        )
        return {"success": True, "item": _item(item)}
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc


@router.post("/deposits/{deposit_id}/reject")
async def admin_deposit_reject(
    deposit_id: str,
    current_admin: User = Depends(get_current_admin),
    db: AsyncSession = Depends(get_db),
):
    try:
        item = await reject_deposit(db, deposit_id=deposit_id)
        return {"success": True, "item": _item(item)}
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc


@router.get("/withdrawals")
async def admin_withdrawals(
    limit: int = Query(default=100, ge=1, le=200),
    current_admin: User = Depends(get_current_admin),
    db: AsyncSession = Depends(get_db),
):
    items = await list_pending_withdrawals(db, limit)
    return {"items": [_item(x) for x in items]}


@router.post("/withdrawals/{withdrawal_id}/approve")
async def admin_withdrawal_approve(
    withdrawal_id: str,
    current_admin: User = Depends(get_current_admin),
    db: AsyncSession = Depends(get_db),
):
    try:
        item = await approve_withdrawal(
            db, withdrawal_id=withdrawal_id,
            admin_telegram_id=current_admin.telegram_id,
        )
        return {"success": True, "item": _item(item)}
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc


@router.post("/withdrawals/{withdrawal_id}/reject")
async def admin_withdrawal_reject(
    withdrawal_id: str,
    current_admin: User = Depends(get_current_admin),
    db: AsyncSession = Depends(get_db),
):
    try:
        item = await reject_withdrawal(db, withdrawal_id=withdrawal_id)
        return {"success": True, "item": _item(item)}
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc


@router.get("/transfers")
async def admin_transfers(
    limit: int = Query(default=100, ge=1, le=200),
    current_admin: User = Depends(get_current_admin),
    db: AsyncSession = Depends(get_db),
):
    items = await list_transfers(db, limit)
    return {"items": [_item(x) for x in items]}
