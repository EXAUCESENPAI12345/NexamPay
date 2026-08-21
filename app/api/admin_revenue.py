from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.admin_dependencies import (
    get_current_admin,
)
from app.database import get_db
from app.models import User
from app.schemas.revenue import (
    RevenueItem,
    RevenueListResponse,
    RevenueSummary,
)
from app.services.admin_revenue_service import (
    get_revenue_report,
)


router = APIRouter(
    prefix="/api/v1/admin/revenue",
    tags=["Admin Revenue"],
)


@router.get(
    "",
    response_model=RevenueListResponse,
)
async def revenue_report(
    page: int = Query(
        default=1,
        ge=1,
    ),
    page_size: int = Query(
        default=20,
        ge=1,
        le=100,
    ),
    revenue_type: str | None = Query(
        default=None,
    ),
    currency_code: str | None = Query(
        default=None,
    ),
    current_admin: User = Depends(
        get_current_admin
    ),
    db: AsyncSession = Depends(get_db),
):
    items, summaries, total = (
        await get_revenue_report(
            db=db,
            page=page,
            page_size=page_size,
            revenue_type=revenue_type,
            currency_code=currency_code,
        )
    )

    return RevenueListResponse(
        items=[
            RevenueItem(
                revenue_id=item.revenue_id,
                revenue_type=getattr(item.revenue_type, "value", item.revenue_type),
                status=getattr(item.status, "value", item.status),
                amount=item.amount,
                currency_code=item.currency_code,
                source_transaction_id=(
                    item.source_transaction_id
                ),
                source_order_id=(
                    item.source_order_id
                ),
                description=item.description,
                created_at=(
                    item.created_at.isoformat()
                ),
            )
            for item in items
        ],
        summaries=[
            RevenueSummary(
                currency_code=item[
                    "currency_code"
                ],
                total_revenue=item[
                    "total_revenue"
                ],
            )
            for item in summaries
        ],
        page=page,
        page_size=page_size,
        total=total,
    )