from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.admin_dependencies import get_current_admin
from app.database import get_db
from app.models import Country, User
from app.schemas.virtual_card import (
    CardApplicationAdminItem,
    CardApprovalRequest,
    CardRejectionRequest,
    VirtualCardResponse,
)
from app.services.virtual_card_service import (
    approve_card_application,
    list_card_applications,
    reject_card_application,
)

router = APIRouter(
    prefix="/api/v1/admin/cards",
    tags=["Admin Virtual Cards"],
)


@router.get("/applications", response_model=list[CardApplicationAdminItem])
async def admin_card_applications(
    status: str | None = Query(default=None),
    limit: int = Query(default=100, ge=1, le=200),
    current_admin: User = Depends(get_current_admin),
    db: AsyncSession = Depends(get_db),
):
    applications = await list_card_applications(
        db,
        status=status,
        limit=limit,
    )

    if not applications:
        return []

    user_ids = {item.user_id for item in applications}
    country_ids = {item.country_id for item in applications}

    users_result = await db.execute(
        select(User).where(User.id.in_(user_ids))
    )
    users = {user.id: user for user in users_result.scalars().all()}

    countries_result = await db.execute(
        select(Country).where(Country.id.in_(country_ids))
    )
    countries = {
        country.id: country
        for country in countries_result.scalars().all()
    }

    return [
        CardApplicationAdminItem(
            application_id=item.application_id,
            user_id=item.user_id,
            nexampay_id=users[item.user_id].nexampay_id,
            telegram_id=users[item.user_id].telegram_id,
            cardholder_name=item.cardholder_name,
            phone_number=item.phone_number,
            country_code=countries[item.country_id].code,
            country_name=countries[item.country_id].name,
            currency_code=item.currency_code,
            status=getattr(item.status, "value", item.status),
            created_at=item.created_at,
            reviewed_at=item.reviewed_at,
            admin_note=item.admin_note,
            rejection_reason=item.rejection_reason,
        )
        for item in applications
    ]


@router.post(
    "/applications/{application_id}/approve",
    response_model=VirtualCardResponse,
)
async def approve(
    application_id: str,
    payload: CardApprovalRequest,
    current_admin: User = Depends(get_current_admin),
    db: AsyncSession = Depends(get_db),
):
    try:
        card = await approve_card_application(
            db,
            application_id=application_id,
            admin_telegram_id=current_admin.telegram_id,
            admin_note=payload.admin_note,
            brand=payload.brand,
            masked_number=payload.masked_number,
            last4=payload.last4,
            expiry_month=payload.expiry_month,
            expiry_year=payload.expiry_year,
            provider_card_id=payload.provider_card_id,
        )
        return VirtualCardResponse(
            card_id=card.card_id,
            status=getattr(card.status, "value", card.status),
            currency_code=card.currency_code,
            brand=card.brand,
            masked_number=card.masked_number,
            last4=card.last4,
            expiry_month=card.expiry_month,
            expiry_year=card.expiry_year,
        )
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc


@router.post("/applications/{application_id}/reject")
async def reject(
    application_id: str,
    payload: CardRejectionRequest,
    current_admin: User = Depends(get_current_admin),
    db: AsyncSession = Depends(get_db),
):
    try:
        application = await reject_card_application(
            db,
            application_id=application_id,
            admin_telegram_id=current_admin.telegram_id,
            reason=payload.reason,
        )
        return {
            "success": True,
            "application_id": application.application_id,
            "status": str(application.status),
            "rejection_reason": application.rejection_reason,
        }
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
