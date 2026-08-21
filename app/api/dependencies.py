from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials
from fastapi.security import HTTPBearer
from sqlalchemy import select
from fastapi import Header
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.models import User
from app.services.session_service import (
    get_user_from_session,
)


security = HTTPBearer(
    auto_error=False
)


async def get_current_user(
    credentials: HTTPAuthorizationCredentials | None = Depends(security),
    telegram_init_data: str | None = Header(
        default=None,
        alias="X-Telegram-Init-Data",
    ),
    db: AsyncSession = Depends(get_db),
) -> User:
    token = None

    if credentials is not None:
        if credentials.scheme.lower() == "bearer":
            token = credentials.credentials
        elif credentials.scheme.lower() == "telegram":
            telegram_init_data = credentials.credentials
        else:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid authentication scheme.",
            )

    if token:
        user = await get_user_from_session(db, token)
        if user is not None:
            return user

    if telegram_init_data:
        from app.services.telegram_auth_service import validate_telegram_init_data
        try:
            telegram_user = validate_telegram_init_data(telegram_init_data)
            telegram_id = int(telegram_user["id"])
        except (ValueError, TypeError) as exc:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid Telegram authentication.",
            ) from exc

        result = await db.execute(
            select(User)
            .where(
                User.telegram_id == telegram_id,
                User.is_active.is_(True),
            )
            .limit(1)
        )
        user = result.scalar_one_or_none()

        if user is not None:
            return user

    raise HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Authentication required.",
    )
