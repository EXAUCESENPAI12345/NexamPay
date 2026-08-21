from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.dependencies import get_current_user
from app.database import get_db
from app.models import User, Wallet
from app.schemas.wallet import WalletResponse


router = APIRouter(
    prefix="/api/v1/wallet",
    tags=["Wallet"],
)


@router.get(
    "",
    response_model=WalletResponse,
)
async def get_wallet(
    current_user: User = Depends(
        get_current_user
    ),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(
        select(Wallet)
        .where(
            Wallet.user_id == current_user.id,
            Wallet.status == "active",
        )
        .limit(1)
    )

    wallet = result.scalar_one_or_none()

    if wallet is None:
        raise HTTPException(
            status_code=404,
            detail="Wallet not found.",
        )

    return WalletResponse(
        balance=wallet.balance,
        currency_code=wallet.currency_code,
        status=wallet.status,
    )