import secrets
from decimal import Decimal, ROUND_DOWN

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models import (
    RevenueType,
    Transaction,
    TransactionStatus,
    TransactionType,
    Transfer,
    TransferStatus,
    User,
    Wallet,
)
from app.services.revenue_service import record_revenue
from app.services.notification_service import send_telegram_message


FEE_RATE = Decimal("0.03")


def calculate_transfer_fee(amount: Decimal) -> Decimal:
    if amount <= 0:
        raise ValueError("Transfer amount must be greater than zero.")
    return (amount * FEE_RATE).quantize(Decimal("0.01"))


def generate_transfer_id() -> str:
    return "TRF-" + secrets.token_hex(8).upper()


def calculate_received_amount(amount: Decimal, rate: Decimal) -> Decimal:
    if rate <= 0:
        raise ValueError("Invalid exchange rate.")
    return (amount * rate).quantize(
        Decimal("0.01"), rounding=ROUND_DOWN
    )


async def create_transfer(
    db: AsyncSession,
    *,
    sender: User,
    receiver_nexampay_id: str,
    amount: Decimal,
    exchange_rate: Decimal,
    idempotency_key: str,
) -> Transfer:
    if amount <= 0:
        raise ValueError("Transfer amount must be greater than zero.")

    if not receiver_nexampay_id.startswith("NXP-") or len(receiver_nexampay_id) != 12:
        raise ValueError("Invalid NexamPay ID.")

    existing_result = await db.execute(
        select(Transfer)
        .where(Transfer.idempotency_key == idempotency_key)
        .limit(1)
    )
    existing = existing_result.scalar_one_or_none()
    if existing is not None:
        if existing.sender_id != sender.id:
            raise ValueError("Invalid idempotency key.")
        return existing

    receiver_result = await db.execute(
        select(User)
        .where(
            User.nexampay_id == receiver_nexampay_id,
            User.is_active.is_(True),
        )
        .limit(1)
    )
    receiver = receiver_result.scalar_one_or_none()
    if receiver is None:
        raise ValueError("Recipient not found.")

    if receiver.id == sender.id:
        raise ValueError("You cannot transfer money to yourself.")

    first_user_id = min(sender.id, receiver.id)
    second_user_id = max(sender.id, receiver.id)

    first_result = await db.execute(
        select(Wallet)
        .where(
            Wallet.user_id == first_user_id,
            Wallet.status == "active",
        )
        .with_for_update()
    )
    first_wallet = first_result.scalar_one_or_none()
    if first_wallet is None:
        raise ValueError("First wallet not found.")

    second_result = await db.execute(
        select(Wallet)
        .where(
            Wallet.user_id == second_user_id,
            Wallet.status == "active",
        )
        .with_for_update()
    )
    second_wallet = second_result.scalar_one_or_none()
    if second_wallet is None:
        raise ValueError("Second wallet not found.")

    if sender.id == first_user_id:
        sender_wallet, receiver_wallet = first_wallet, second_wallet
    else:
        sender_wallet, receiver_wallet = second_wallet, first_wallet

    fee = calculate_transfer_fee(amount)
    total_debited = amount + fee
    effective_rate = (
        Decimal("1")
        if sender_wallet.currency_code == receiver_wallet.currency_code
        else exchange_rate
    )
    amount_received = calculate_received_amount(amount, effective_rate)

    available_balance = sender_wallet.balance - sender_wallet.reserved_balance
    if available_balance < total_debited:
        raise ValueError("Insufficient available balance.")

    transaction_idempotency_key = f"transfer:{idempotency_key}"
    transaction_result = await db.execute(
        select(Transaction)
        .where(Transaction.idempotency_key == transaction_idempotency_key)
        .limit(1)
    )
    existing_transaction = transaction_result.scalar_one_or_none()
    if existing_transaction is not None:
        raise ValueError("Transfer transaction already exists.")

    transaction = Transaction(
        transaction_id="TRX-" + secrets.token_hex(8).upper(),
        user_id=sender.id,
        type=TransactionType.TRANSFER,
        status=TransactionStatus.COMPLETED,
        amount=amount,
        fee=fee,
        total_amount=total_debited,
        currency_code=sender_wallet.currency_code,
        provider="nexampay_internal",
        description=f"Transfer to {receiver.nexampay_id}",
        idempotency_key=transaction_idempotency_key,
    )
    db.add(transaction)
    await db.flush()

    transfer = Transfer(
        transfer_id=generate_transfer_id(),
        idempotency_key=idempotency_key,
        transaction_id=transaction.id,
        sender_id=sender.id,
        receiver_id=receiver.id,
        sender_currency=sender_wallet.currency_code,
        receiver_currency=receiver_wallet.currency_code,
        amount_sent=amount,
        fee=fee,
        total_debited=total_debited,
        exchange_rate=effective_rate,
        amount_received=amount_received,
        status=TransferStatus.COMPLETED,
    )
    db.add(transfer)

    sender_wallet.balance -= total_debited
    receiver_wallet.balance += amount_received

    if fee > Decimal("0"):
        await record_revenue(
            db,
            revenue_type=RevenueType.TRANSFER_FEE,
            amount=fee,
            currency_code=sender_wallet.currency_code,
            source_transaction_id=transaction.id,
            description="NexamPay transfer commission",
        )

    await db.commit()
    await db.refresh(transfer)

    await send_telegram_message(
        telegram_id=sender.telegram_id,
        text=(
            f"✅ Transfert NexamPay effectué\n"
            f"Référence : {transfer.transfer_id}\n"
            f"Montant : {transfer.amount_sent} {transfer.sender_currency}\n"
            f"Destinataire : {receiver.nexampay_id}"
        ),
    )
    await send_telegram_message(
        telegram_id=receiver.telegram_id,
        text=(
            f"💰 Vous avez reçu un transfert NexamPay\n"
            f"Référence : {transfer.transfer_id}\n"
            f"Montant : {transfer.amount_received} {transfer.receiver_currency}"
        ),
    )
    return transfer
