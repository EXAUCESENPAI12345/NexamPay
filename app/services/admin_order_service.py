from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models import Order


async def get_admin_orders(
    db: AsyncSession,
    *,
    page: int,
    page_size: int,
    status: str | None = None,
    delivery_status: str | None = None,
    order_number: str | None = None,
):
    conditions = []

    if status:
        conditions.append(Order.status == status)

    if delivery_status:
        conditions.append(Order.delivery_status == delivery_status)

    if order_number:
        conditions.append(Order.order_number == order_number)

    total_result = await db.execute(
        select(func.count(Order.id)).where(*conditions)
    )
    total = total_result.scalar_one()

    offset = (page - 1) * page_size
    result = await db.execute(
        select(Order)
        .where(*conditions)
        .order_by(Order.created_at.desc())
        .offset(offset)
        .limit(page_size)
    )

    return list(result.scalars().all()), total


from decimal import Decimal
from datetime import datetime, timezone

from app.models import (
    OrderItem,
    OrderStatus,
    DeliveryStatus,
    Product,
    Transaction,
    TransactionStatus,
    TransactionType,
    RevenueType,
    User,
)
from app.services.revenue_service import record_revenue
from app.services.transaction_service import generate_transaction_id
from app.services.wallet_service import get_wallet_for_update
from app.services.notification_service import send_telegram_message


async def approve_order(db: AsyncSession, *, order_number: str) -> Order:
    result = await db.execute(
        select(Order)
        .where(Order.order_number == order_number)
        .with_for_update()
    )
    order = result.scalar_one_or_none()
    if order is None:
        raise ValueError("Order not found.")

    if order.status in (OrderStatus.PAID, OrderStatus.PROCESSING, OrderStatus.COMPLETED):
        return order

    if order.status != OrderStatus.PENDING_PAYMENT:
        raise ValueError("Order is not awaiting administrator validation.")

    item_result = await db.execute(
        select(OrderItem)
        .where(OrderItem.order_id == order.id)
        .order_by(OrderItem.id.asc())
        .limit(1)
    )
    item = item_result.scalar_one_or_none()
    if item is None:
        raise ValueError("Order item not found.")

    product_result = await db.execute(
        select(Product)
        .where(Product.id == item.product_id, Product.is_active.is_(True))
        .with_for_update()
    )
    product = product_result.scalar_one_or_none()
    if product is None:
        raise ValueError("Product is unavailable.")
    if product.stock < item.quantity:
        raise ValueError("Insufficient product stock.")

    wallet = await get_wallet_for_update(db, order.user_id)
    if wallet.currency_code != order.currency_code:
        raise ValueError("Order currency does not match wallet currency.")
    if wallet.balance < order.total_amount:
        raise ValueError("Insufficient wallet balance.")

    transaction = Transaction(
        transaction_id=generate_transaction_id(),
        user_id=order.user_id,
        type=TransactionType.PURCHASE,
        status=TransactionStatus.COMPLETED,
        amount=order.total_amount,
        fee=Decimal("0.00"),
        total_amount=order.total_amount,
        currency_code=order.currency_code,
        provider="nexampay_wallet",
        idempotency_key=f"order:{order.order_number}",
        description=f"Purchase: {item.product_name}",
        completed_at=datetime.now(timezone.utc),
    )
    db.add(transaction)
    await db.flush()

    order.payment_transaction_id = transaction.id
    order.status = OrderStatus.PAID
    order.delivery_status = DeliveryStatus.PROCESSING
    product.stock -= item.quantity
    wallet.balance -= order.total_amount

    await record_revenue(
        db,
        revenue_type=RevenueType.PRODUCT_SALE,
        amount=order.total_amount,
        currency_code=order.currency_code,
        source_transaction_id=transaction.id,
        source_order_id=order.id,
        description=f"Product sale: {item.product_name}",
    )

    await db.commit()
    await db.refresh(order)

    user = await db.scalar(select(User).where(User.id == order.user_id))
    if user is not None:
        await send_telegram_message(
            telegram_id=user.telegram_id,
            text=(
                f"✅ Commande NexamPay validée\n"
                f"Commande : {order.order_number}\n"
                f"Montant : {order.total_amount} {order.currency_code}"
            ),
        )
    return order


async def reject_order(
    db: AsyncSession,
    *,
    order_number: str,
    reason: str | None = None,
) -> Order:
    result = await db.execute(
        select(Order)
        .where(Order.order_number == order_number)
        .with_for_update()
    )
    order = result.scalar_one_or_none()
    if order is None:
        raise ValueError("Order not found.")

    if order.status != OrderStatus.PENDING_PAYMENT:
        raise ValueError("Order is no longer awaiting validation.")

    order.status = OrderStatus.CANCELLED
    order.delivery_status = DeliveryStatus.FAILED
    await db.commit()
    await db.refresh(order)

    user = await db.scalar(select(User).where(User.id == order.user_id))
    if user is not None:
        await send_telegram_message(
            telegram_id=user.telegram_id,
            text=(
                f"❌ Commande NexamPay refusée\n"
                f"Commande : {order.order_number}"
            ),
        )
    return order
