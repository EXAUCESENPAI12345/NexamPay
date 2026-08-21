import secrets

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models import User


async def generate_unique_nexampay_id(
    db: AsyncSession,
) -> str:
    """Generate the public NexamPay ID format NXP-12345678."""
    while True:
        identifier = f"NXP-{secrets.randbelow(100_000_000):08d}"

        result = await db.execute(
            select(User.id)
            .where(User.nexampay_id == identifier)
            .limit(1)
        )

        if result.scalar_one_or_none() is None:
            return identifier
