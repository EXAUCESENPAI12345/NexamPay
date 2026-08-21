from fastapi import (
    APIRouter,
    Depends,
    HTTPException,
    Query,
)
from sqlalchemy import func, select, update
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.dependencies import get_current_user
from app.database import get_db
from app.models import Notification, User
from app.schemas.notification import (
    NotificationItem,
    NotificationListResponse,
)


router = APIRouter(
    prefix="/api/v1/notifications",
    tags=["Notifications"],
)


@router.get(
    "",
    response_model=NotificationListResponse,
)
async def get_notifications(
    page: int = Query(
        default=1,
        ge=1,
    ),
    page_size: int = Query(
        default=20,
        ge=1,
        le=100,
    ),
    current_user: User = Depends(
        get_current_user
    ),
    db: AsyncSession = Depends(get_db),
):
    base_condition = (
        Notification.user_id
        == current_user.id
    )

    total_result = await db.execute(
        select(
            func.count(Notification.id)
        )
        .where(base_condition)
    )

    total = total_result.scalar_one()

    unread_result = await db.execute(
        select(
            func.count(Notification.id)
        )
        .where(
            base_condition,
            Notification.is_read.is_(False),
        )
    )

    unread_count = (
        unread_result.scalar_one()
    )

    offset = (
        page - 1
    ) * page_size

    result = await db.execute(
        select(Notification)
        .where(base_condition)
        .order_by(
            Notification.created_at.desc()
        )
        .offset(offset)
        .limit(page_size)
    )

    notifications = list(
        result.scalars().all()
    )

    return NotificationListResponse(
        items=[
            NotificationItem(
                id=item.id,
                type=item.type,
                title=item.title,
                message=item.message,
                reference_id=(
                    item.reference_id
                ),
                is_read=item.is_read,
                created_at=(
                    item.created_at.isoformat()
                ),
            )
            for item in notifications
        ],
        unread_count=unread_count,
        page=page,
        page_size=page_size,
        total=total,
    )
    
    
@router.post(
    "/{notification_id}/read"
)
async def mark_notification_read(
    notification_id: int,
    current_user: User = Depends(
        get_current_user
    ),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(
        select(Notification)
        .where(
            Notification.id
            == notification_id,
            Notification.user_id
            == current_user.id,
        )
        .limit(1)
    )

    notification = (
        result.scalar_one_or_none()
    )

    if notification is None:
        raise HTTPException(
            status_code=404,
            detail="Notification not found.",
        )

    notification.is_read = True

    await db.commit()

    return {
        "success": True
    }
    
@router.post("/read-all")
async def mark_all_read(
    current_user: User = Depends(
        get_current_user
    ),
    db: AsyncSession = Depends(get_db),
):
    await db.execute(
        update(Notification)
        .where(
            Notification.user_id
            == current_user.id,
            Notification.is_read.is_(False),
        )
        .values(is_read=True)
    )

    await db.commit()

    return {
        "success": True
    }