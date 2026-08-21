import hashlib
import hmac
import json
import time
from urllib.parse import parse_qsl

from app.config import settings


MAX_INIT_DATA_AGE = 300


def validate_telegram_init_data(
    init_data: str,
) -> dict:

    if not init_data:
        raise ValueError(
            "Telegram initData is required."
        )

    parsed = dict(
        parse_qsl(
            init_data,
            keep_blank_values=True,
        )
    )

    received_hash = parsed.pop(
        "hash",
        None,
    )

    if not received_hash:
        raise ValueError(
            "Telegram initData hash is missing."
        )

    auth_date = parsed.get("auth_date")

    if not auth_date:
        raise ValueError(
            "Telegram auth_date is missing."
        )

    try:
        auth_timestamp = int(auth_date)
    except ValueError as exc:
        raise ValueError(
            "Invalid Telegram auth_date."
        ) from exc

    current_timestamp = int(time.time())

    if (
        current_timestamp - auth_timestamp
        > MAX_INIT_DATA_AGE
    ):
        raise ValueError(
            "Telegram initData has expired."
        )

    data_check_string = "\n".join(
        f"{key}={value}"
        for key, value in sorted(
            parsed.items()
        )
    )

    secret_key = hmac.new(
        b"WebAppData",
        settings.telegram_bot_token.encode(
            "utf-8"
        ),
        hashlib.sha256,
    ).digest()

    calculated_hash = hmac.new(
        secret_key,
        data_check_string.encode("utf-8"),
        hashlib.sha256,
    ).hexdigest()

    if not hmac.compare_digest(
        calculated_hash,
        received_hash,
    ):
        raise ValueError(
            "Invalid Telegram initData."
        )

    user_json = parsed.get("user")

    if not user_json:
        raise ValueError(
            "Telegram user data is missing."
        )

    try:
        telegram_user = json.loads(
            user_json
        )
    except json.JSONDecodeError as exc:
        raise ValueError(
            "Invalid Telegram user data."
        ) from exc

    telegram_id = telegram_user.get("id")

    if not telegram_id:
        raise ValueError(
            "Telegram user ID is missing."
        )

    return telegram_user