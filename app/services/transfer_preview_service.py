from decimal import Decimal

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models import User, Wallet
from app.services.currency_service import (
    get_exchange_rate,
)
from app.services.transfer_service import (
    calculate_received_amount,
    calculate_transfer_fee,
)


async def preview_transfer(
    db: AsyncSession,
    *,
    sender: User,
    receiver_nexampay_id: str,
    amount: Decimal,
):
    receiver_result = await db.execute(
        select(User)
        .where(
            User.nexampay_id
            == receiver_nexampay_id,
            User.is_active.is_(True),
        )
        .limit(1)
    )

    receiver = (
        receiver_result.scalar_one_or_none()
    )

    if receiver is None:
        raise ValueError(
            "Recipient not found."
        )

    if receiver.id == sender.id:
        raise ValueError(
            "You cannot transfer money to yourself."
        )

    sender_wallet_result = await db.execute(
        select(Wallet)
        .where(
            Wallet.user_id == sender.id,
            Wallet.status == "active",
        )
        .limit(1)
    )

    sender_wallet = (
        sender_wallet_result
        .scalar_one_or_none()
    )

    if sender_wallet is None:
        raise ValueError(
            "Sender wallet not found."
        )

    receiver_wallet_result = await db.execute(
        select(Wallet)
        .where(
            Wallet.user_id == receiver.id,
            Wallet.status == "active",
        )
        .limit(1)
    )

    receiver_wallet = (
        receiver_wallet_result
        .scalar_one_or_none()
    )

    if receiver_wallet is None:
        raise ValueError(
            "Recipient wallet not found."
        )

    fee = calculate_transfer_fee(
        amount
    )

    total_debited = amount + fee

    available_balance = (
        sender_wallet.balance
        - sender_wallet.reserved_balance
    )

    if available_balance < total_debited:
        raise ValueError(
            "Insufficient available balance."
        )

    exchange_rate = await get_exchange_rate(
        db,
        from_currency=(
            sender_wallet.currency_code
        ),
        to_currency=(
            receiver_wallet.currency_code
        ),
    )

    amount_received = (
        calculate_received_amount(
            amount,
            exchange_rate,
        )
    )

    return {
        "receiver_nexampay_id": (
            receiver.nexampay_id
        ),
        "amount_sent": amount,
        "fee": fee,
        "total_debited": total_debited,
        "amount_received": amount_received,
        "sender_currency": (
            sender_wallet.currency_code
        ),
        "receiver_currency": (
            receiver_wallet.currency_code
        ),
        "exchange_rate": exchange_rate,
    }