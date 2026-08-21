from fastapi import APIRouter, Depends
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.models import Country


router = APIRouter(
    prefix="/api/v1/countries",
    tags=["Countries"],
)


@router.get("")
async def get_countries(
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(
        select(Country)
        .where(
            Country.is_active.is_(True)
        )
        .order_by(
            Country.name.asc()
        )
    )

    countries = result.scalars().all()

    return {
        "items": [
            {
                "id": country.id,
                "code": country.code,
                "name": country.name,
                "currency_code": (
                    country.currency_code
                ),
                "flag_code": (
                    country.flag_code
                ),
            }
            for country in countries
        ]
    }