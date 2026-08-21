from fastapi import APIRouter, Depends
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.models import MobileMoneyNetwork


router = APIRouter(
    prefix="/api/v1/mobile-money",
    tags=["Mobile Money"],
)


@router.get(
    "/networks/{country_id}"
)
async def get_networks(
    country_id: int,
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(
        select(MobileMoneyNetwork)
        .where(
            MobileMoneyNetwork.country_id
            == country_id,
            MobileMoneyNetwork.is_active.is_(
                True
            ),
        )
        .order_by(
            MobileMoneyNetwork.name.asc()
        )
    )

    networks = result.scalars().all()

    return {
        "items": [
            {
                "id": network.id,
                "code": network.code,
                "name": network.name,
                "logo_url": (
                    network.logo_url
                ),
                "currency_code": (
                    network.currency_code
                ),
            }
            for network in networks
        ]
    }