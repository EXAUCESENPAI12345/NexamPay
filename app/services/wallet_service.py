from decimal import Decimal

from fastapi import HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models import Wallet


async def get_wallet_for_update(
    db: AsyncSession,
    user_id: int,
) -> Wallet:
    result = await db.execute(
        select(Wallet)
        .where(
            Wallet.user_id == user_id,
            Wallet.status == "active",
        )
        .with_for_update()
    )

    wallet = result.scalar_one_or_none()

    if wallet is None:
        raise HTTPException(
            status_code=404,
            detail="Wallet not found.",
        )

    return wallet


async def credit_wallet(
    wallet: Wallet,
    amount: Decimal,
) -> None:
    if amount <= 0:
        raise HTTPException(
            status_code=400,
            detail="Amount must be greater than zero.",
        )

    wallet.balance += amount


async def debit_wallet(
    wallet: Wallet,
    amount: Decimal,
) -> None:
    if amount <= 0:
        raise HTTPException(
            status_code=400,
            detail="Amount must be greater than zero.",
        )

    if wallet.balance < amount:
        raise HTTPException(
            status_code=400,
            detail="Insufficient wallet balance.",
        )

    wallet.balance -= amount