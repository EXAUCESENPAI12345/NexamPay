from fastapi import APIRouter, Depends
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.dependencies import get_current_user
from app.database import get_db
from app.models import User, UserSettings
from app.schemas.settings import SettingsResponse, SettingsUpdateRequest

router = APIRouter(prefix="/api/v1/settings", tags=["Settings"])


async def _get_or_create(db: AsyncSession, user: User) -> UserSettings:
    result = await db.execute(select(UserSettings).where(UserSettings.user_id == user.id).limit(1))
    settings = result.scalar_one_or_none()
    if settings is None:
        settings = UserSettings(user_id=user.id)
        db.add(settings)
        await db.flush()
    return settings


@router.get("", response_model=SettingsResponse)
async def get_settings(current_user: User = Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    settings = await _get_or_create(db, current_user)
    await db.commit()
    return SettingsResponse(
        language=settings.language,
        currency_code=settings.currency_code,
        color=settings.color,
        theme=settings.theme,
        bot_notifications_enabled=settings.bot_notifications_enabled,
    )


@router.patch("", response_model=SettingsResponse)
async def update_settings(
    payload: SettingsUpdateRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    settings = await _get_or_create(db, current_user)
    changes = payload.model_dump(exclude_unset=True)
    for key, value in changes.items():
        setattr(settings, key, value)
    await db.commit()
    return SettingsResponse(
        language=settings.language,
        currency_code=settings.currency_code,
        color=settings.color,
        theme=settings.theme,
        bot_notifications_enabled=settings.bot_notifications_enabled,
    )
