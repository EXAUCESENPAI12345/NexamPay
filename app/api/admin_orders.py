from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.admin_dependencies import get_current_admin
from app.database import get_db
from app.models import User
from app.schemas.admin_order import (
    OrderAdminItem,
    OrderAdminListResponse,
)
from app.services.admin_order_service import (
    get_admin_orders,
    approve_order,
    reject_order,
)


router = APIRouter(
    prefix="/api/v1/admin/orders",
    tags=["Admin Orders"],
)


@router.get("", response_model=OrderAdminListResponse)
async def orders(
    page: int = Query(default=1, ge=1),
    page_size: int = Query(default=20, ge=1, le=100),
    status: str | None = Query(default=None),
    delivery_status: str | None = Query(default=None),
    order_number: str | None = Query(default=None),
    current_admin: User = Depends(get_current_admin),
    db: AsyncSession = Depends(get_db),
):
    items, total = await get_admin_orders(
        db=db,
        page=page,
        page_size=page_size,
        status=status,
        delivery_status=delivery_status,
        order_number=order_number,
    )

    return OrderAdminListResponse(
        items=[
            OrderAdminItem(
                order_number=order.order_number,
                user_id=order.user_id,
                status=getattr(order.status, "value", order.status),
                delivery_status=getattr(order.delivery_status, "value", order.delivery_status),
                total_amount=order.total_amount,
                currency_code=order.currency_code,
                created_at=order.created_at.isoformat(),
            )
            for order in items
        ],
        page=page,
        page_size=page_size,
        total=total,
    )


@router.post("/{order_number}/approve")
async def approve_admin_order(
    order_number: str,
    current_admin: User = Depends(get_current_admin),
    db: AsyncSession = Depends(get_db),
):
    try:
        order = await approve_order(db, order_number=order_number)
        return {
            "success": True,
            "order_number": order.order_number,
            "status": getattr(order.status, "value", order.status),
            "delivery_status": getattr(order.delivery_status, "value", order.delivery_status),
        }
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc


@router.post("/{order_number}/reject")
async def reject_admin_order(
    order_number: str,
    current_admin: User = Depends(get_current_admin),
    db: AsyncSession = Depends(get_db),
):
    try:
        order = await reject_order(db, order_number=order_number)
        return {
            "success": True,
            "order_number": order.order_number,
            "status": getattr(order.status, "value", order.status),
        }
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
