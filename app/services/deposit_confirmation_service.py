from datetime import datetime, timezone
from decimal import Decimal

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models import (
    DepositRequest,
    DepositStatus,
    User,
    Transaction,
    TransactionStatus,
    TransactionType,
    Wallet,
)
from app.services.revenue_service import (
    record_revenue,
)
from app.services.notification_service import send_telegram_message
from app.models import RevenueType


async def confirm_deposit(
    db: AsyncSession,
    *,
    provider_transaction_id: str,
    provider_status: str,
) -> DepositRequest:

    result = await db.execute(
        select(DepositRequest)
        .where(
            DepositRequest.provider_transaction_id
            == provider_transaction_id
        )
        .with_for_update()
    )

    deposit = result.scalar_one_or_none()

    if deposit is None:
        raise ValueError(
            "Deposit request not found."
        )

    # Idempotence :
    # un webhook déjà traité ne doit pas
    # créditer le Wallet une deuxième fois.
    if deposit.status == DepositStatus.COMPLETED:
        return deposit

    if provider_status != "completed":
        deposit.status = DepositStatus.FAILED

        await db.commit()

        return deposit

    wallet_result = await db.execute(
        select(Wallet)
        .where(
            Wallet.user_id == deposit.user_id,
            Wallet.currency_code
            == deposit.currency_code,
            Wallet.status == "active",
        )
        .with_for_update()
    )

    wallet = wallet_result.scalar_one_or_none()

    if wallet is None:
        raise ValueError(
            "Wallet not found."
        )

    transaction_idempotency_key = (
        f"deposit:{provider_transaction_id}"
    )

    existing_transaction_result = await db.execute(
        select(Transaction)
        .where(
            Transaction.idempotency_key
            == transaction_idempotency_key
        )
        .limit(1)
    )
    existing_transaction = (
        existing_transaction_result.scalar_one_or_none()
    )

    if existing_transaction is not None:
        deposit.status = DepositStatus.COMPLETED
        await db.commit()
        await db.refresh(deposit)
        return deposit

    transaction = Transaction(
        transaction_id=(
            f"DEP-{provider_transaction_id}"
        ),
        user_id=deposit.user_id,
        type=TransactionType.DEPOSIT,
        status=TransactionStatus.COMPLETED,
        amount=deposit.amount,
        fee=deposit.fee,
        total_amount=deposit.total_amount,
        currency_code=deposit.currency_code,
        provider="mobile_fusion",
        description="NexamPay deposit",
        idempotency_key=transaction_idempotency_key,
    )

    db.add(transaction)

    await db.flush()

    # Seul le montant du dépôt est crédité
    # dans le Wallet.
    wallet.balance += deposit.amount

    deposit.status = DepositStatus.COMPLETED

    await db.flush()

    if deposit.fee > Decimal("0"):
        await record_revenue(
            db,
            revenue_type=RevenueType.DEPOSIT_FEE,
            amount=deposit.fee,
            currency_code=deposit.currency_code,
            source_transaction_id=transaction.id,
            description=(
                "NexamPay deposit commission"
            ),
        )

    await db.commit()
    await db.refresh(deposit)

    user_result = await db.execute(
        select(User).where(User.id == deposit.user_id).limit(1)
    )
    user = user_result.scalar_one_or_none()
    if user is not None:
        await send_telegram_message(
            telegram_id=user.telegram_id,
            text=(
                f"✅ Dépôt NexamPay confirmé\n"
                f"Référence : {deposit.deposit_id}\n"
                f"Montant : {deposit.amount} {deposit.currency_code}"
            ),
        )

    return deposit