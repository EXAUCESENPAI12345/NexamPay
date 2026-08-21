from fastapi import Depends, HTTPException, status

from app.api.dependencies import get_current_user
from app.config import settings
from app.models import User


async def get_current_admin(
    current_user: User = Depends(get_current_user),
) -> User:
    if settings.admin_telegram_id is None:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Admin account is not configured.",
        )

    if current_user.telegram_id != settings.admin_telegram_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Administrator access required.",
        )

    return current_user
