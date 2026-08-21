import secrets
from decimal import Decimal

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.services.fee_service import calculate_fee

from app.models import (
    Country,
    MobileMoneyNetwork,
    User,
    Wallet,
    WithdrawalRequest,
    WithdrawalStatus,
)



def calculate_withdrawal_fee(amount: Decimal) -> Decimal:
    return calculate_fee(amount)


def generate_withdrawal_id() -> str:
    return (
        "WTH-"
        + secrets.token_hex(8).upper()
    )


async def create_withdrawal(
    db: AsyncSession,
    *,
    user: User,
    country_id: int,
    network_id: int,
    phone_number: str,
    amount: Decimal,
) -> WithdrawalRequest:

    if amount <= 0:
        raise ValueError(
            "Amount must be greater than zero."
        )

    if not phone_number.strip():
        raise ValueError(
            "Mobile Money number is required."
        )

    country_result = await db.execute(
        select(Country)
        .where(
            Country.id == country_id,
            Country.is_active.is_(True),
        )
        .limit(1)
    )

    country = country_result.scalar_one_or_none()

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

    network = network_result.scalar_one_or_none()

    if network is None:
        raise ValueError(
            "Selected network is unavailable."
        )

    if network.country_id != country.id:
        raise ValueError(
            "Network does not belong to selected country."
        )

    if network.currency_code != country.currency_code:
        raise ValueError(
            "Network currency does not match country currency."
        )

    if amount.as_tuple().exponent < -2:
        raise ValueError(
            "Amount has too many decimal places."
        )

    fee = calculate_withdrawal_fee(amount)

    total_debited = amount + fee

    wallet_result = await db.execute(
        select(Wallet)
        .where(
            Wallet.user_id == user.id,
            Wallet.currency_code
            == country.currency_code,
            Wallet.status == "active",
        )
        .with_for_update()
        .limit(1)
    )

    wallet = wallet_result.scalar_one_or_none()

    if wallet is None:
        raise ValueError(
            "Wallet not found."
        )

    if wallet.balance < total_debited:
        raise ValueError(
            "Insufficient wallet balance."
        )

    withdrawal = WithdrawalRequest(
        withdrawal_id=generate_withdrawal_id(),
        user_id=user.id,
        country_id=country.id,
        network_id=network.id,
        phone_number=phone_number.strip(),
        amount=amount,
        fee=fee,
        total_debited=total_debited,
        currency_code=country.currency_code,
        status=WithdrawalStatus.PENDING,
    )

    db.add(withdrawal)

    await db.flush()

    # Réservation financière :
    # les fonds restent dans le solde comptable,
    # mais deviennent indisponibles jusqu'au résultat
    # du prestataire.
    wallet.reserved_balance += total_debited

    await db.commit()
    await db.refresh(withdrawal)

    return withdrawal