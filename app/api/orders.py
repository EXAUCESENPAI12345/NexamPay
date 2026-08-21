from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.dependencies import get_current_user
from app.database import get_db
from app.models import OrderItem, User
from app.schemas.order import (
    CreateOrderRequest,
    OrderResponse,
)
from app.services.order_service import (
    create_paid_order,
)


router = APIRouter(
    prefix="/api/v1/orders",
    tags=["Orders"],
)


@router.post(
    "",
    response_model=OrderResponse,
)
async def create_order(
    payload: CreateOrderRequest,
    current_user: User = Depends(
        get_current_user
    ),
    db: AsyncSession = Depends(get_db),
):
    try:
        order = await create_paid_order(
            db=db,
            user=current_user,
            product_id=payload.product_id,
            quantity=payload.quantity,
            idempotency_key=(
                payload.idempotency_key
            ),
        )

    except ValueError as exc:
        raise HTTPException(
            status_code=400,
            detail=str(exc),
        ) from exc

    item_result = await db.execute(
        select(OrderItem)
        .where(OrderItem.order_id == order.id)
        .order_by(OrderItem.id.asc())
        .limit(1)
    )
    item = item_result.scalar_one_or_none()

    if item is None:
        raise HTTPException(
            status_code=500,
            detail="Order item not found.",
        )

    return OrderResponse(
        order_number=order.order_number,
        status=order.status,
        delivery_status=order.delivery_status,
        product_name=item.product_name,
        quantity=item.quantity,
        total_amount=order.total_amount,
        currency_code=order.currency_code,
    )