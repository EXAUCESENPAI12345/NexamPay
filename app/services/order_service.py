import secrets
from decimal import Decimal

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models import (
    Order,
    OrderItem,
    OrderStatus,
    DeliveryStatus,
    Product,
    Transaction,
    TransactionStatus,
    TransactionType,
    User,
    RevenueType,
)
from app.services.revenue_service import record_revenue
from app.services.transaction_service import (
    generate_transaction_id,
)
from app.services.wallet_service import (
    get_wallet_for_update,
)


def generate_order_number() -> str:
    return (
        "ORD-"
        + secrets.token_hex(6).upper()
    )


async def create_paid_order(
    db: AsyncSession,
    *,
    user: User,
    product_id: int,
    quantity: int,
    idempotency_key: str,
) -> Order:
    if quantity <= 0:
        raise ValueError("Quantity must be greater than zero.")

    # Prevent duplicate order submissions by storing the client key on the
    # order only after checking existing orders. A unique payment transaction
    # is created later, when the administrator approves the order.
    existing_order = await db.scalar(
        select(Order)
        .where(Order.idempotency_key == idempotency_key)
        .limit(1)
    )
    if existing_order is not None:
        if existing_order.user_id != user.id:
            raise ValueError("Invalid idempotency key.")
        return existing_order

    product_result = await db.execute(
        select(Product)
        .where(
            Product.id == product_id,
            Product.is_active.is_(True),
        )
        .limit(1)
    )
    product = product_result.scalar_one_or_none()

    if product is None:
        raise ValueError("Product is unavailable.")

    if product.stock < quantity:
        raise ValueError("Insufficient product stock.")

    wallet = await get_wallet_for_update(db, user.id)

    if wallet.currency_code != product.currency_code:
        raise ValueError("Product currency does not match wallet currency.")

    subtotal = product.price * Decimal(quantity)

    order = Order(
        order_number=generate_order_number(),
        idempotency_key=idempotency_key,
        user_id=user.id,
        total_amount=subtotal,
        currency_code=product.currency_code,
        status=OrderStatus.PENDING_PAYMENT,
        delivery_status=DeliveryStatus.PENDING,
        payment_transaction_id=None,
    )
    db.add(order)
    await db.flush()

    item = OrderItem(
        order_id=order.id,
        product_id=product.id,
        product_name=product.name,
        unit_price=product.price,
        quantity=quantity,
        subtotal=subtotal,
    )
    db.add(item)

    await db.commit()
    await db.refresh(order)
    return order
