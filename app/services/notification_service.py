from sqlalchemy.ext.asyncio import AsyncSession

from app.models import (
    Notification,
    NotificationType,
)


async def create_notification(
    db: AsyncSession,
    *,
    user_id: int,
    notification_type: NotificationType,
    title: str,
    message: str,
    reference_id: str | None = None,
) -> Notification:

    notification = Notification(
        user_id=user_id,
        type=notification_type,
        title=title,
        message=message,
        reference_id=reference_id,
        is_read=False,
    )

    db.add(notification)

    await db.flush()

    return notification

async def send_telegram_message(
    *,
    telegram_id: int,
    text: str,
) -> bool:
    """Best-effort Telegram Bot notification.

    Financial state is committed before this network call. A Telegram delivery
    failure therefore never rolls back a successful transaction.
    """
    import httpx
    from app.config import settings

    if not settings.telegram_bot_token:
        return False

    url = (
        f"https://api.telegram.org/bot"
        f"{settings.telegram_bot_token}/sendMessage"
    )
    try:
        async with httpx.AsyncClient(timeout=8.0) as client:
            response = await client.post(
                url,
                json={
                    "chat_id": telegram_id,
                    "text": text,
                    "disable_web_page_preview": True,
                },
            )
            return response.is_success
    except httpx.HTTPError:
        return False
