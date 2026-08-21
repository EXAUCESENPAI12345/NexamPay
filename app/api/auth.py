from fastapi import APIRouter, Depends, Header, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.schemas.auth import (
    AuthResponse,
    CreateAccountRequest,
    TelegramAuthRequest,
)
from app.services.auth_service import (
    authenticate_telegram,
    create_account,
)
from app.services.session_service import revoke_session

router = APIRouter(
    prefix="/api/v1/auth",
    tags=["Authentication"],
)


@router.post(
    "/telegram",
)
async def telegram_login(
    payload: TelegramAuthRequest,
    db: AsyncSession = Depends(get_db),
):
    try:
        return await authenticate_telegram(
            db,
            init_data=payload.init_data,
        )

    except ValueError as exc:
        raise HTTPException(
            status_code=401,
            detail=str(exc),
        ) from exc


@router.post(
    "/telegram/create-account",
)
async def telegram_create_account(
    payload: CreateAccountRequest,
    db: AsyncSession = Depends(get_db),
):
    try:
        result = await create_account(
            db,
            init_data=payload.init_data,
            country_id=payload.country_id,
            network_id=payload.network_id,
            pin=payload.pin,
        )

        return {
            "success": True,
            "session_token": (
                result["session_token"]
            ),
            "nexampay_id": (
                result["user"].nexampay_id
            ),
            "currency_code": (
                result["wallet"].currency_code
            ),
        }

    except ValueError as exc:
        raise HTTPException(
            status_code=400,
            detail=str(exc),
        ) from exc
        
@router.post("/logout")
async def logout(
    authorization: str | None = Header(
        default=None
    ),
    db: AsyncSession = Depends(get_db),
):
    if not authorization:
        return {
            "success": True
        }

    parts = authorization.split(
        " ",
        1,
    )

    if (
        len(parts) != 2
        or parts[0].lower() != "bearer"
    ):
        return {
            "success": True
        }

    await revoke_session(
        db,
        parts[1],
    )

    return {
        "success": True
    }