import hashlib
import secrets
from datetime import datetime, timedelta, timezone

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models import User, UserSession


SESSION_DURATION_HOURS = 24


def hash_session_token(token: str) -> str:
    return hashlib.sha256(
        token.encode("utf-8")
    ).hexdigest()


async def create_session(
    db: AsyncSession,
    user: User,
) -> str:
    token = secrets.token_urlsafe(48)

    token_hash = hash_session_token(token)

    expires_at = (
        datetime.now(timezone.utc)
        + timedelta(hours=SESSION_DURATION_HOURS)
    )

    session = UserSession(
        user_id=user.id,
        token_hash=token_hash,
        expires_at=expires_at,
    )

    db.add(session)

    await db.commit()

    return token


async def get_user_from_session(
    db: AsyncSession,
    token: str,
) -> User | None:

    token_hash = hash_session_token(token)

    result = await db.execute(
        select(UserSession)
        .where(
            UserSession.token_hash == token_hash,
            UserSession.revoked_at.is_(None),
            UserSession.expires_at > datetime.now(
                timezone.utc
            ),
        )
        .limit(1)
    )

    session = result.scalar_one_or_none()

    if session is None:
        return None

    user_result = await db.execute(
        select(User)
        .where(
            User.id == session.user_id,
            User.is_active.is_(True),
        )
        .limit(1)
    )

    return user_result.scalar_one_or_none()


async def revoke_session(
    db: AsyncSession,
    token: str,
) -> None:

    token_hash = hash_session_token(token)

    result = await db.execute(
        select(UserSession)
        .where(
            UserSession.token_hash == token_hash,
            UserSession.revoked_at.is_(None),
        )
        .limit(1)
    )

    session = result.scalar_one_or_none()

    if session is not None:
        session.revoked_at = datetime.now(
            timezone.utc
        )

        await db.commit()