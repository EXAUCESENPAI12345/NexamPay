from datetime import datetime, timezone
from decimal import Decimal

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models import (
    DepositRequest,
    Transaction,
    TransactionStatus,
    Wallet,
)
from app.services.wallet_service import credit_wallet


async def complete_deposit(
    db: AsyncSession,
    *,
    transaction_id: str,
    provider_reference: str,
) -> Transaction:

    result = await db.execute(
        select(Transaction)
        .where(
            Transaction.transaction_id == transaction_id
        )
        .with_for_update()
    )

    transaction = result.scalar_one_or_none()

    if transaction is None:
        raise ValueError("Transaction not found.")

    if transaction.type != "deposit":
        raise ValueError(
            "Transaction is not a deposit."
        )

    if transaction.status == TransactionStatus.COMPLETED:
        return transaction

    if transaction.status in {
        TransactionStatus.CANCELLED,
        TransactionStatus.FAILED,
        TransactionStatus.REFUNDED,
    }:
        raise ValueError(
            "Transaction can no longer be completed."
        )

    deposit_result = await db.execute(
        select(DepositRequest)
        .where(
            DepositRequest.transaction_id == transaction.id
        )
        .with_for_update()
    )

    deposit = deposit_result.scalar_one_or_none()

    if deposit is None:
        raise ValueError(
            "Deposit request not found."
        )

    existing_provider_result = await db.execute(
        select(DepositRequest)
        .where(
            DepositRequest.provider_reference
            == provider_reference,
            DepositRequest.id != deposit.id,
        )
        .limit(1)
    )

    existing_provider = (
        existing_provider_result.scalar_one_or_none()
    )

    if existing_provider is not None:
        raise ValueError(
            "Provider reference already belongs to another deposit."
        )

    wallet_result = await db.execute(
        select(Wallet)
        .where(
            Wallet.user_id == transaction.user_id,
            Wallet.currency_code
            == transaction.currency_code,
            Wallet.is_active.is_(True),
        )
        .with_for_update()
    )

    wallet = wallet_result.scalar_one_or_none()

    if wallet is None:
        raise ValueError(
            "Matching wallet not found."
        )

    deposit.provider_reference = provider_reference

    transaction.status = TransactionStatus.COMPLETED
    transaction.completed_at = datetime.now(
        timezone.utc
    )

    await credit_wallet(
        wallet,
        Decimal(transaction.amount),
    )

    await db.commit()
    await db.refresh(transaction)

    return transaction