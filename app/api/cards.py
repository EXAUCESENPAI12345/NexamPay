from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.dependencies import get_current_user
from app.database import get_db
from app.models import User, VirtualCardStatus
from app.schemas.virtual_card import (
    CardApplicationCreateRequest,
    CardApplicationResponse,
    VirtualCardResponse,
)
from app.services.virtual_card_service import (
    create_card_application,
    get_my_application,
    get_my_card,
    set_card_status,
)

router = APIRouter(
    prefix="/api/v1/cards",
    tags=["Virtual Cards"],
)


def _application_response(application):
    return CardApplicationResponse(
        application_id=application.application_id,
        status=getattr(application.status, "value", application.status),
        cardholder_name=application.cardholder_name,
        phone_number=application.phone_number,
        currency_code=application.currency_code,
        admin_note=application.admin_note,
        rejection_reason=application.rejection_reason,
        reviewed_at=application.reviewed_at,
    )


def _card_response(card):
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


@router.post("/applications", response_model=CardApplicationResponse)
async def apply_for_virtual_card(
    payload: CardApplicationCreateRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    try:
        application = await create_card_application(
            db,
            user=current_user,
            country_id=payload.country_id,
            cardholder_name=payload.cardholder_name,
            phone_number=payload.phone_number,
        )
        return _application_response(application)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc


@router.get("/application", response_model=CardApplicationResponse | None)
async def my_card_application(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    application = await get_my_application(db, user=current_user)
    return _application_response(application) if application else None


@router.get("/me", response_model=VirtualCardResponse | None)
async def my_virtual_card(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    card = await get_my_card(db, user=current_user)
    return _card_response(card) if card else None


@router.post("/{card_id}/freeze", response_model=VirtualCardResponse)
async def freeze_virtual_card(
    card_id: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    try:
        card = await set_card_status(
            db,
            user=current_user,
            card_id=card_id,
            status=VirtualCardStatus.FROZEN,
        )
        return _card_response(card)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc


@router.post("/{card_id}/unfreeze", response_model=VirtualCardResponse)
async def unfreeze_virtual_card(
    card_id: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    try:
        card = await set_card_status(
            db,
            user=current_user,
            card_id=card_id,
            status=VirtualCardStatus.ACTIVE,
        )
        return _card_response(card)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
