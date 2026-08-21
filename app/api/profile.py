from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.dependencies import get_current_user
from app.database import get_db
from app.models import Country, MobileMoneyNetwork, User, Wallet
from app.schemas.profile import (
    ProfileResponse,
    WalletResponse,
)


router = APIRouter(
    prefix="/api/v1/profile",
    tags=["Profile"],
)


@router.get(
    "",
    response_model=ProfileResponse,
)
async def profile(
    current_user: User = Depends(
        get_current_user
    ),
    db: AsyncSession = Depends(get_db),
):
    country_result = await db.execute(
        select(Country)
        .where(
            Country.id
            == current_user.country_id
        )
        .limit(1)
    )

    country = country_result.scalar_one_or_none()

    if country is None:
        raise HTTPException(
            status_code=500,
            detail="User country not found.",
        )

    network = None
    if current_user.network_id is not None:
        network_result = await db.execute(
            select(MobileMoneyNetwork)
            .where(MobileMoneyNetwork.id == current_user.network_id)
            .limit(1)
        )
        network = network_result.scalar_one_or_none()

    wallet_result = await db.execute(
        select(Wallet)
        .where(
            Wallet.user_id
            == current_user.id,
            Wallet.status == "active",
        )
        .limit(1)
    )

    wallet = wallet_result.scalar_one_or_none()

    if wallet is None:
        raise HTTPException(
            status_code=500,
            detail="User wallet not found.",
        )

    return ProfileResponse(
        nexampay_id=current_user.nexampay_id,
        telegram_username=(
            current_user.telegram_username
        ),
        first_name=current_user.first_name,
        last_name=current_user.last_name,
        photo_url=current_user.photo_url,
        country_code=country.code,
        country_name=country.name,
        currency_code=(
            country.currency_code
        ),
        network_id=current_user.network_id,
        network_code=network.code if network else None,
        network_name=network.name if network else None,
        wallet=WalletResponse(
            balance=wallet.balance,
            currency_code=wallet.currency_code,
            status=wallet.status,
        ),
    )