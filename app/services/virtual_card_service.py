import secrets
from datetime import datetime, timezone

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models import (
    Country,
    User,
    VirtualCard,
    VirtualCardApplication,
    VirtualCardApplicationStatus,
    VirtualCardStatus,
)


def generate_application_id() -> str:
    return "VCA-" + secrets.token_hex(8).upper()


def generate_card_id() -> str:
    return "NXC-" + secrets.token_hex(8).upper()


async def create_card_application(
    db: AsyncSession,
    *,
    user: User,
    country_id: int,
    cardholder_name: str,
    phone_number: str,
) -> VirtualCardApplication:
    country_result = await db.execute(
        select(Country).where(
            Country.id == country_id,
            Country.is_active.is_(True),
        ).limit(1)
    )
    country = country_result.scalar_one_or_none()
    if country is None:
        raise ValueError("Selected country is unavailable.")

    if not cardholder_name.strip():
        raise ValueError("Cardholder name is required.")

    if not phone_number.strip():
        raise ValueError("Phone number is required.")

    existing = await db.execute(
        select(VirtualCardApplication).where(
            VirtualCardApplication.user_id == user.id,
            VirtualCardApplication.status.in_([
                VirtualCardApplicationStatus.PENDING,
                VirtualCardApplicationStatus.APPROVED,
            ]),
        ).limit(1)
    )
    if existing.scalar_one_or_none() is not None:
        raise ValueError(
            "You already have a pending or approved virtual card application."
        )

    active_card = await db.execute(
        select(VirtualCard).where(
            VirtualCard.user_id == user.id,
            VirtualCard.status.in_([
                VirtualCardStatus.ACTIVE,
                VirtualCardStatus.FROZEN,
            ]),
        ).limit(1)
    )
    if active_card.scalar_one_or_none() is not None:
        raise ValueError("You already have an active virtual card.")

    application = VirtualCardApplication(
        application_id=generate_application_id(),
        user_id=user.id,
        country_id=country.id,
        cardholder_name=cardholder_name.strip(),
        phone_number=phone_number.strip(),
        currency_code=country.currency_code,
        status=VirtualCardApplicationStatus.PENDING,
    )
    db.add(application)
    await db.commit()
    await db.refresh(application)
    return application


async def get_my_application(
    db: AsyncSession,
    *,
    user: User,
) -> VirtualCardApplication | None:
    result = await db.execute(
        select(VirtualCardApplication)
        .where(
            VirtualCardApplication.user_id == user.id
        )
        .order_by(VirtualCardApplication.created_at.desc())
        .limit(1)
    )
    return result.scalar_one_or_none()


async def get_my_card(
    db: AsyncSession,
    *,
    user: User,
) -> VirtualCard | None:
    result = await db.execute(
        select(VirtualCard)
        .where(
            VirtualCard.user_id == user.id,
            VirtualCard.status != VirtualCardStatus.CLOSED,
        )
        .order_by(VirtualCard.created_at.desc())
        .limit(1)
    )
    return result.scalar_one_or_none()


async def list_card_applications(
    db: AsyncSession,
    *,
    status: str | None = None,
    limit: int = 100,
) -> list[VirtualCardApplication]:
    query = select(VirtualCardApplication).order_by(
        VirtualCardApplication.created_at.desc()
    ).limit(limit)
    if status:
        query = query.where(
            VirtualCardApplication.status == status
        )
    result = await db.execute(query)
    return list(result.scalars().all())


async def approve_card_application(
    db: AsyncSession,
    *,
    application_id: str,
    admin_telegram_id: int,
    admin_note: str | None = None,
    brand: str | None = None,
    masked_number: str | None = None,
    last4: str | None = None,
    expiry_month: int | None = None,
    expiry_year: int | None = None,
    provider_card_id: str | None = None,
) -> VirtualCard:
    result = await db.execute(
        select(VirtualCardApplication)
        .where(
            VirtualCardApplication.application_id == application_id
        )
        .with_for_update()
    )
    application = result.scalar_one_or_none()
    if application is None:
        raise ValueError("Card application not found.")

    if application.status != VirtualCardApplicationStatus.PENDING:
        raise ValueError("Card application is not pending.")

    existing_card_result = await db.execute(
        select(VirtualCard).where(
            VirtualCard.user_id == application.user_id,
            VirtualCard.status.in_([
                VirtualCardStatus.ACTIVE,
                VirtualCardStatus.FROZEN,
            ]),
        ).limit(1)
    )
    if existing_card_result.scalar_one_or_none() is not None:
        raise ValueError("User already has an active virtual card.")

    card = VirtualCard(
        card_id=generate_card_id(),
        application_id=application.id,
        user_id=application.user_id,
        currency_code=application.currency_code,
        brand=brand,
        masked_number=masked_number,
        last4=last4,
        expiry_month=expiry_month,
        expiry_year=expiry_year,
        provider_card_id=provider_card_id,
        status=VirtualCardStatus.ACTIVE,
    )
    db.add(card)

    application.status = VirtualCardApplicationStatus.APPROVED
    application.admin_note = admin_note
    application.reviewed_by_telegram_id = admin_telegram_id
    application.reviewed_at = datetime.now(timezone.utc)

    await db.commit()
    await db.refresh(card)
    return card


async def reject_card_application(
    db: AsyncSession,
    *,
    application_id: str,
    admin_telegram_id: int,
    reason: str,
) -> VirtualCardApplication:
    result = await db.execute(
        select(VirtualCardApplication)
        .where(
            VirtualCardApplication.application_id == application_id
        )
        .with_for_update()
    )
    application = result.scalar_one_or_none()
    if application is None:
        raise ValueError("Card application not found.")

    if application.status != VirtualCardApplicationStatus.PENDING:
        raise ValueError("Card application is not pending.")

    application.status = VirtualCardApplicationStatus.REJECTED
    application.rejection_reason = reason.strip()
    application.reviewed_by_telegram_id = admin_telegram_id
    application.reviewed_at = datetime.now(timezone.utc)

    await db.commit()
    await db.refresh(application)
    return application


async def set_card_status(
    db: AsyncSession,
    *,
    user: User,
    card_id: str,
    status: VirtualCardStatus,
) -> VirtualCard:
    result = await db.execute(
        select(VirtualCard)
        .where(
            VirtualCard.card_id == card_id,
            VirtualCard.user_id == user.id,
        )
        .with_for_update()
    )
    card = result.scalar_one_or_none()
    if card is None:
        raise ValueError("Virtual card not found.")

    if card.status == VirtualCardStatus.CLOSED:
        raise ValueError("Closed card cannot be changed.")

    card.status = status
    await db.commit()
    await db.refresh(card)
    return card
