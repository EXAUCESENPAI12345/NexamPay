from datetime import datetime, timezone

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models import (
    DeliveryStatus,
    Order,
    OrderDelivery,
    OrderStatus,
    User,
)
from app.services.telegram_delivery_service import (
    telegram_delivery_service,
)


async def deliver_order(
    db: AsyncSession,
    *,
    order_number: str,
    delivery_text: str,
) -> Order:

    result = await db.execute(
        select(Order)
        .where(
            Order.order_number == order_number
        )
        .with_for_update()
    )

    order = result.scalar_one_or_none()

    if order is None:
        raise ValueError(
            "Order not found."
        )

    if order.status != OrderStatus.PROCESSING:
        raise ValueError(
            "Order must be processing before delivery."
        )

    existing_result = await db.execute(
        select(OrderDelivery)
        .where(
            OrderDelivery.order_id == order.id
        )
        .limit(1)
    )

    existing_delivery = (
        existing_result.scalar_one_or_none()
    )

    if (
        existing_delivery is not None
        and existing_delivery.status
        == "delivered"
    ):
        raise ValueError(
            "Order has already been delivered."
        )

    user_result = await db.execute(
        select(User)
        .where(
            User.id == order.user_id,
            User.is_active.is_(True),
        )
        .limit(1)
    )

    user = user_result.scalar_one_or_none()

    if user is None:
        raise ValueError(
            "Order owner not found."
        )

    if existing_delivery is None:
        delivery = OrderDelivery(
            order_id=order.id,
            telegram_user_id=user.telegram_id,
            delivery_type="telegram_private",
            status="processing",
        )

        db.add(delivery)

    else:
        delivery = existing_delivery
        delivery.telegram_user_id = user.telegram_id
        delivery.status = "processing"
        delivery.error_message = None

    await db.flush()

    try:
        telegram_message = (
            await telegram_delivery_service.send_text(
                telegram_user_id=user.telegram_id,
                text=delivery_text,
            )
        )

    except Exception as exc:
        delivery.status = "failed"
        delivery.error_message = str(exc)

        await db.commit()

        raise ValueError(
            "Telegram delivery failed."
        ) from exc

    delivery.status = "delivered"
    delivery.message_id = telegram_message["message_id"]
    delivery.delivered_at = datetime.now(
        timezone.utc
    )

    order.delivery_status = (
        DeliveryStatus.DELIVERED
    )

    order.status = OrderStatus.COMPLETED

    await db.commit()
    await db.refresh(order)

    return order