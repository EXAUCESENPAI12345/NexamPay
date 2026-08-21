from datetime import datetime, timezone
from decimal import Decimal

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models import (
    DepositRequest,
    DepositStatus,
    Order,
    Product,
    Transaction,
    TransactionStatus,
    TransactionType,
    User,
    Wallet,
    WithdrawalRequest,
    WithdrawalStatus,
    RevenueType,
)
from app.services.revenue_service import record_revenue
from app.services.notification_service import send_telegram_message


async def get_admin_stats(db: AsyncSession) -> dict:
    users = await db.scalar(select(func.count(User.id)))
    deposits = await db.scalar(
        select(func.count(DepositRequest.id)).where(
            DepositRequest.status == DepositStatus.PENDING
        )
    )
    withdrawals = await db.scalar(
        select(func.count(WithdrawalRequest.id)).where(
            WithdrawalRequest.status == WithdrawalStatus.PENDING
        )
    )
    orders = await db.scalar(
        select(func.count(Order.id)).where(
            Order.status.in_(["paid", "processing"])
        )
    )
    products = await db.scalar(
        select(func.count(Product.id)).where(Product.is_active.is_(True))
    )
    return {
        "users": users or 0,
        "pending_deposits": deposits or 0,
        "pending_withdrawals": withdrawals or 0,
        "pending_orders": orders or 0,
        "active_products": products or 0,
    }


async def list_pending_deposits(db: AsyncSession, limit: int = 100):
    result = await db.execute(
        select(DepositRequest)
        .where(DepositRequest.status == DepositStatus.PENDING)
        .order_by(DepositRequest.created_at.asc())
        .limit(limit)
    )
    return list(result.scalars().all())


async def list_pending_withdrawals(db: AsyncSession, limit: int = 100):
    result = await db.execute(
        select(WithdrawalRequest)
        .where(WithdrawalRequest.status == WithdrawalStatus.PENDING)
        .order_by(WithdrawalRequest.created_at.asc())
        .limit(limit)
    )
    return list(result.scalars().all())


async def list_transfers(db: AsyncSession, limit: int = 100):
    from app.models import Transfer
    result = await db.execute(
        select(Transfer)
        .order_by(Transfer.created_at.desc())
        .limit(limit)
    )
    return list(result.scalars().all())


async def approve_deposit(
    db: AsyncSession, *, deposit_id: str, admin_telegram_id: int
):
    result = await db.execute(
        select(DepositRequest)
        .where(DepositRequest.deposit_id == deposit_id)
        .with_for_update()
    )
    deposit = result.scalar_one_or_none()
    if deposit is None:
        raise ValueError("Deposit request not found.")
    if deposit.status == DepositStatus.COMPLETED:
        return deposit
    if deposit.status != DepositStatus.PENDING:
        raise ValueError("Deposit request is no longer pending.")

    wallet_result = await db.execute(
        select(Wallet)
        .where(
            Wallet.user_id == deposit.user_id,
            Wallet.currency_code == deposit.currency_code,
            Wallet.status == "active",
        )
        .with_for_update()
    )
    wallet = wallet_result.scalar_one_or_none()
    if wallet is None:
        raise ValueError("Wallet not found.")

    idem = f"admin:deposit:{deposit.deposit_id}"
    existing = await db.scalar(
        select(Transaction).where(Transaction.idempotency_key == idem)
    )
    if existing is None:
        transaction = Transaction(
            transaction_id=f"DEP-{deposit.deposit_id}",
            user_id=deposit.user_id,
            type=TransactionType.DEPOSIT,
            status=TransactionStatus.COMPLETED,
            amount=deposit.amount,
            fee=deposit.fee,
            total_amount=deposit.total_amount,
            currency_code=deposit.currency_code,
            provider="nexampay_admin",
            description="NexamPay deposit validated by administrator",
            idempotency_key=idem,
            completed_at=datetime.now(timezone.utc),
        )
        db.add(transaction)
        await db.flush()
        wallet.balance += deposit.amount
        if deposit.fee > Decimal("0"):
            await record_revenue(
                db,
                revenue_type=RevenueType.DEPOSIT_FEE,
                amount=deposit.fee,
                currency_code=deposit.currency_code,
                source_transaction_id=transaction.id,
                description="NexamPay deposit commission",
            )
    deposit.status = DepositStatus.COMPLETED
    await db.commit()
    await db.refresh(deposit)

    user = await db.scalar(select(User).where(User.id == deposit.user_id))
    if user is not None:
        await send_telegram_message(
            telegram_id=user.telegram_id,
            text=(
                f"✅ Dépôt NexamPay validé\n"
                f"Référence : {deposit.deposit_id}\n"
                f"Montant : {deposit.amount} {deposit.currency_code}"
            ),
        )
    return deposit


async def reject_deposit(
    db: AsyncSession, *, deposit_id: str, reason: str | None = None
):
    result = await db.execute(
        select(DepositRequest)
        .where(DepositRequest.deposit_id == deposit_id)
        .with_for_update()
    )
    deposit = result.scalar_one_or_none()
    if deposit is None:
        raise ValueError("Deposit request not found.")
    if deposit.status != DepositStatus.PENDING:
        raise ValueError("Deposit request is no longer pending.")
    deposit.status = DepositStatus.FAILED
    deposit.failure_reason = reason or "Rejected by administrator."
    await db.commit()
    await db.refresh(deposit)

    user = await db.scalar(select(User).where(User.id == deposit.user_id))
    if user is not None:
        await send_telegram_message(
            telegram_id=user.telegram_id,
            text=(
                f"❌ Dépôt NexamPay refusé\n"
                f"Référence : {deposit.deposit_id}"
            ),
        )
    return deposit


async def approve_withdrawal(
    db: AsyncSession, *, withdrawal_id: str, admin_telegram_id: int
):
    result = await db.execute(
        select(WithdrawalRequest)
        .where(WithdrawalRequest.withdrawal_id == withdrawal_id)
        .with_for_update()
    )
    withdrawal = result.scalar_one_or_none()
    if withdrawal is None:
        raise ValueError("Withdrawal request not found.")
    if withdrawal.status == WithdrawalStatus.COMPLETED:
        return withdrawal
    if withdrawal.status != WithdrawalStatus.PENDING:
        raise ValueError("Withdrawal request is no longer pending.")

    wallet_result = await db.execute(
        select(Wallet)
        .where(
            Wallet.user_id == withdrawal.user_id,
            Wallet.currency_code == withdrawal.currency_code,
            Wallet.status == "active",
        )
        .with_for_update()
    )
    wallet = wallet_result.scalar_one_or_none()
    if wallet is None:
        raise ValueError("Wallet not found.")
    if wallet.reserved_balance < withdrawal.total_debited:
        raise ValueError("Reserved withdrawal balance is inconsistent.")

    idem = f"admin:withdrawal:{withdrawal.withdrawal_id}"
    existing = await db.scalar(
        select(Transaction).where(Transaction.idempotency_key == idem)
    )
    if existing is None:
        transaction = Transaction(
            transaction_id=f"WTH-{withdrawal.withdrawal_id}",
            user_id=withdrawal.user_id,
            type=TransactionType.WITHDRAWAL,
            status=TransactionStatus.COMPLETED,
            amount=withdrawal.amount,
            fee=withdrawal.fee,
            total_amount=withdrawal.total_debited,
            currency_code=withdrawal.currency_code,
            provider="nexampay_admin",
            description="NexamPay withdrawal validated by administrator",
            idempotency_key=idem,
            completed_at=datetime.now(timezone.utc),
        )
        db.add(transaction)
        await db.flush()
        wallet.balance -= withdrawal.total_debited
        wallet.reserved_balance -= withdrawal.total_debited
        if withdrawal.fee > Decimal("0"):
            await record_revenue(
                db,
                revenue_type=RevenueType.WITHDRAWAL_FEE,
                amount=withdrawal.fee,
                currency_code=withdrawal.currency_code,
                source_transaction_id=transaction.id,
                description="NexamPay withdrawal commission",
            )
    withdrawal.status = WithdrawalStatus.COMPLETED
    await db.commit()
    await db.refresh(withdrawal)

    user = await db.scalar(select(User).where(User.id == withdrawal.user_id))
    if user is not None:
        await send_telegram_message(
            telegram_id=user.telegram_id,
            text=(
                f"✅ Retrait NexamPay validé\n"
                f"Référence : {withdrawal.withdrawal_id}\n"
                f"Montant : {withdrawal.amount} {withdrawal.currency_code}"
            ),
        )
    return withdrawal


async def reject_withdrawal(
    db: AsyncSession, *, withdrawal_id: str, reason: str | None = None
):
    result = await db.execute(
        select(WithdrawalRequest)
        .where(WithdrawalRequest.withdrawal_id == withdrawal_id)
        .with_for_update()
    )
    withdrawal = result.scalar_one_or_none()
    if withdrawal is None:
        raise ValueError("Withdrawal request not found.")
    if withdrawal.status != WithdrawalStatus.PENDING:
        raise ValueError("Withdrawal request is no longer pending.")

    wallet_result = await db.execute(
        select(Wallet)
        .where(
            Wallet.user_id == withdrawal.user_id,
            Wallet.currency_code == withdrawal.currency_code,
            Wallet.status == "active",
        )
        .with_for_update()
    )
    wallet = wallet_result.scalar_one_or_none()
    if wallet is None:
        raise ValueError("Wallet not found.")
    if wallet.reserved_balance < withdrawal.total_debited:
        raise ValueError("Reserved withdrawal balance is inconsistent.")

    wallet.reserved_balance -= withdrawal.total_debited
    withdrawal.status = WithdrawalStatus.CANCELLED
    withdrawal.failure_reason = reason or "Rejected by administrator."
    await db.commit()
    await db.refresh(withdrawal)

    user = await db.scalar(select(User).where(User.id == withdrawal.user_id))
    if user is not None:
        await send_telegram_message(
            telegram_id=user.telegram_id,
            text=(
                f"❌ Retrait NexamPay refusé\n"
                f"Référence : {withdrawal.withdrawal_id}"
            ),
        )
    return withdrawal
