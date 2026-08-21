from decimal import Decimal

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models import (
    RevenueType,
    Transaction,
    TransactionStatus,
    TransactionType,
    Wallet,
    WithdrawalRequest,
    WithdrawalStatus,
    User,
)
from app.services.revenue_service import record_revenue
from app.services.notification_service import send_telegram_message


async def process_withdrawal_result(
    db: AsyncSession,
    *,
    provider_transaction_id: str,
    provider_status: str,
) -> WithdrawalRequest:

    result = await db.execute(
        select(WithdrawalRequest)
        .where(
            WithdrawalRequest.provider_transaction_id
            == provider_transaction_id
        )
        .with_for_update()
    )

    withdrawal = result.scalar_one_or_none()

    if withdrawal is None:
        raise ValueError(
            "Withdrawal request not found."
        )

    # Protection contre les webhooks répétés.
    if withdrawal.status in (
        WithdrawalStatus.COMPLETED,
        WithdrawalStatus.FAILED,
        WithdrawalStatus.CANCELLED,
    ):
        return withdrawal

    wallet_result = await db.execute(
        select(Wallet)
        .where(
            Wallet.user_id == withdrawal.user_id,
            Wallet.currency_code
            == withdrawal.currency_code,
            Wallet.status == "active",
        )
        .with_for_update()
    )

    wallet = wallet_result.scalar_one_or_none()

    if wallet is None:
        raise ValueError(
            "Wallet not found."
        )

    reserved = withdrawal.total_debited

    if wallet.reserved_balance < reserved:
        raise ValueError(
            "Invalid reserved balance."
        )

    if provider_status == "completed":

        wallet.reserved_balance -= reserved
        wallet.balance -= reserved

        transaction_idempotency_key = (
            f"withdrawal:{provider_transaction_id}"
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
            withdrawal.status = WithdrawalStatus.COMPLETED
            await db.commit()
            await db.refresh(withdrawal)
            return withdrawal

        transaction = Transaction(
            transaction_id=(
                f"WTH-{provider_transaction_id}"
            ),
            user_id=withdrawal.user_id,
            type=TransactionType.WITHDRAWAL,
            status=TransactionStatus.COMPLETED,
            amount=withdrawal.amount,
            fee=withdrawal.fee,
            total_amount=withdrawal.total_debited,
            currency_code=withdrawal.currency_code,
            provider="mobile_fusion",
            description="NexamPay withdrawal",
            idempotency_key=transaction_idempotency_key,
        )

        db.add(transaction)

        await db.flush()

        withdrawal.status = (
            WithdrawalStatus.COMPLETED
        )

        if withdrawal.fee > Decimal("0"):
            await record_revenue(
                db,
                revenue_type=(
                    RevenueType.WITHDRAWAL_FEE
                ),
                amount=withdrawal.fee,
                currency_code=(
                    withdrawal.currency_code
                ),
                source_transaction_id=(
                    transaction.id
                ),
                description=(
                    "NexamPay withdrawal commission"
                ),
            )

    else:
        # Le prestataire a refusé/échoué :
        # les fonds réservés retournent
        # automatiquement dans le solde disponible.
        wallet.reserved_balance -= reserved

        withdrawal.status = (
            WithdrawalStatus.FAILED
        )

        withdrawal.failure_reason = (
            "Withdrawal rejected by provider."
        )

    await db.commit()
    await db.refresh(withdrawal)

    user = await db.scalar(
        select(User).where(User.id == withdrawal.user_id).limit(1)
    )
    if user is not None:
        if withdrawal.status == WithdrawalStatus.COMPLETED:
            message = (
                f"✅ Retrait NexamPay confirmé\n"
                f"Référence : {withdrawal.withdrawal_id}\n"
                f"Montant : {withdrawal.amount} {withdrawal.currency_code}"
            )
        else:
            message = (
                f"❌ Retrait NexamPay échoué\n"
                f"Référence : {withdrawal.withdrawal_id}"
            )
        await send_telegram_message(
            telegram_id=user.telegram_id,
            text=message,
        )

    return withdrawal