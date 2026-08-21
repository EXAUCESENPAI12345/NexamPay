import secrets
from decimal import Decimal

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models import (
    Country,
    DepositRequest,
    DepositStatus,
    MobileMoneyNetwork,
    User,
)


FREE_LIMIT = Decimal("1500")
FEE_RATE = Decimal("0.05")


def calculate_deposit_fee(
    amount: Decimal,
) -> Decimal:
    if amount <= FREE_LIMIT:
        return Decimal("0.00")

    return (
        amount * FEE_RATE
    ).quantize(Decimal("0.01"))


def generate_deposit_id() -> str:
    return (
        "DEP-"
        + secrets.token_hex(8).upper()
    )


async def create_deposit(
    db: AsyncSession,
    *,
    user: User,
    country_id: int,
    network_id: int,
    phone_number: str,
    amount: Decimal,
) -> DepositRequest:

    if amount <= 0:
        raise ValueError(
            "Amount must be greater than zero."
        )

    country_result = await db.execute(
        select(Country)
        .where(
            Country.id == country_id,
            Country.is_active.is_(True),
        )
        .limit(1)
    )

    country = (
        country_result.scalar_one_or_none()
    )

    if country is None:
        raise ValueError(
            "Selected country is unavailable."
        )

    network_result = await db.execute(
        select(MobileMoneyNetwork)
        .where(
            MobileMoneyNetwork.id == network_id,
            MobileMoneyNetwork.is_active.is_(True),
        )
        .limit(1)
    )

    network = (
        network_result.scalar_one_or_none()
    )

    if network is None:
        raise ValueError(
            "Selected network is unavailable."
        )

    if network.country_id != country.id:
        raise ValueError(
            "Network does not belong to selected country."
        )

    if not network.currency_code:
        raise ValueError(
            "Network currency is not configured."
        )

    if network.currency_code != country.currency_code:
        raise ValueError(
            "Network currency does not match country currency."
        )

    if not phone_number.strip():
        raise ValueError(
            "Mobile Money number is required."
        )

    fee = calculate_deposit_fee(
        amount
    )

    total_amount = amount + fee

    deposit = DepositRequest(
        deposit_id=generate_deposit_id(),
        user_id=user.id,
        country_id=country.id,
        network_id=network.id,
        phone_number=phone_number.strip(),
        amount=amount,
        fee=fee,
        total_amount=total_amount,
        currency_code=country.currency_code,
        status=DepositStatus.PENDING,
        provider=None,
    )

    db.add(deposit)

    await db.commit()
    await db.refresh(deposit)

    return deposit