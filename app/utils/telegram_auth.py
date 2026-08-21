import hashlib
import hmac
import time
from urllib.parse import parse_qsl

from fastapi import HTTPException, status

from app.config import settings


def validate_telegram_init_data(
    init_data: str,
) -> dict[str, str]:
    if not init_data:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Telegram authentication data is required.",
        )

    try:
        parsed = dict(parse_qsl(init_data, keep_blank_values=True))
    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid Telegram authentication data.",
        ) from exc

    received_hash = parsed.pop("hash", None)

    if not received_hash:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Telegram authentication hash is missing.",
        )

    auth_date = parsed.get("auth_date")

    if not auth_date:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Telegram authentication date is missing.",
        )

    try:
        auth_timestamp = int(auth_date)
    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid Telegram authentication date.",
        ) from exc

    current_timestamp = int(time.time())

    if current_timestamp - auth_timestamp > 86400:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Telegram authentication data has expired.",
        )

    data_check_string = "\n".join(
        f"{key}={value}"
        for key, value in sorted(parsed.items())
    )

    secret_key = hmac.new(
        b"WebAppData",
        settings.telegram_bot_token.encode(),
        hashlib.sha256,
    ).digest()

    calculated_hash = hmac.new(
        secret_key,
        data_check_string.encode(),
        hashlib.sha256,
    ).hexdigest()

    if not hmac.compare_digest(
        calculated_hash,
        received_hash,
    ):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid Telegram authentication.",
        )

    return parsed