from sqlalchemy import select
import hashlib
import secrets
from sqlalchemy.ext.asyncio import AsyncSession

from app.models import MobileMoneyNetwork, User, UserSettings, Wallet
from app.services.identity_service import (
    generate_unique_nexampay_id,
)
from app.services.session_service import (
    create_session,
)
from app.services.telegram_auth_service import (
    validate_telegram_init_data,
)
from app.services.notification_service import send_telegram_message


async def authenticate_telegram(
    db: AsyncSession,
    *,
    init_data: str,
):
    telegram_user = validate_telegram_init_data(
        init_data
    )

    telegram_id = int(
        telegram_user["id"]
    )

    result = await db.execute(
        select(User)
        .where(
            User.telegram_id == telegram_id
        )
        .limit(1)
    )

    user = result.scalar_one_or_none()

    if user is not None:
        session_token = await create_session(
            db,
            user,
        )

        return {
            "is_new_user": False,
            "requires_country": False,
            "session_token": session_token,
            "nexampay_id": user.nexampay_id,
            "telegram_id": telegram_id,
        }

    return {
        "is_new_user": True,
        "requires_country": True,
        "session_token": None,
        "nexampay_id": None,
        "telegram_id": telegram_id,
        "telegram_user": telegram_user,
    }


def hash_pin(pin: str) -> str:
    salt = secrets.token_bytes(16)
    digest = hashlib.pbkdf2_hmac(
        "sha256",
        pin.encode("utf-8"),
        salt,
        120_000,
    )
    return f"pbkdf2_sha256$120000${salt.hex()}${digest.hex()}"


async def create_account(
    db: AsyncSession,
    *,
    init_data: str,
    country_id: int,
    network_id: int | None,
    pin: str,
):
    telegram_user = validate_telegram_init_data(
        init_data
    )

    telegram_id = int(
        telegram_user["id"]
    )

    existing_result = await db.execute(
        select(User)
        .where(
            User.telegram_id == telegram_id
        )
        .limit(1)
    )

    if existing_result.scalar_one_or_none():
        raise ValueError(
            "NexamPay account already exists."
        )

    from app.models import Country

    country_result = await db.execute(
        select(Country)
        .where(
            Country.id == country_id,
            Country.is_active.is_(True),
        )
        .limit(1)
    )

    country = (
        country_result.scalar_one_or_none()
    )

    if country is None:
        raise ValueError(
            "Selected country is unavailable."
        )

    selected_network = None
    if network_id is not None:
        network_result = await db.execute(
            select(MobileMoneyNetwork)
            .where(
                MobileMoneyNetwork.id == network_id,
                MobileMoneyNetwork.country_id == country.id,
                MobileMoneyNetwork.is_active.is_(True),
            )
            .limit(1)
        )
        selected_network = network_result.scalar_one_or_none()
        if selected_network is None:
            raise ValueError(
                "Selected mobile money network is unavailable for this country."
            )

    nexampay_id = (
        await generate_unique_nexampay_id(db)
    )

    user = User(
        telegram_id=telegram_id,
        telegram_username=telegram_user.get(
            "username"
        ),
        first_name=telegram_user.get(
            "first_name"
        ),
        last_name=telegram_user.get(
            "last_name"
        ),
        photo_url=telegram_user.get("photo_url"),
        pin_hash=hash_pin(pin),
        nexampay_id=nexampay_id,
        country_id=country.id,
        network_id=selected_network.id if selected_network else None,
        is_active=True,
    )

    db.add(user)

    await db.flush()

    wallet = Wallet(
        user_id=user.id,
        currency_code=country.currency_code,
        balance=0,
        reserved_balance=0,
        status="active",
    )

    db.add(wallet)

    user_settings = UserSettings(
        user_id=user.id,
        language="fr",
        currency_code=country.currency_code,
        color="nexam",
        theme="dark",
        bot_notifications_enabled=True,
    )
    db.add(user_settings)

    await db.flush()

    session_token = await create_session(
        db,
        user,
    )

    try:
        await send_telegram_message(
            telegram_id=telegram_id,
            text=(
                "✅ <b>Bienvenue sur NexamPay</b>\n\n"
                f"Votre compte a été créé avec succès.\n"
                f"NexamPay Number : <b>{user.nexampay_id}</b>\n"
                f"Solde initial : <b>0 {wallet.currency_code}</b>"
            ),
        )
    except Exception:
        pass

    return {
        "user": user,
        "wallet": wallet,
        "session_token": session_token,
    }