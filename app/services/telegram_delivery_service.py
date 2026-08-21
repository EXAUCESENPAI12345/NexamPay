from typing import Any

import httpx

from app.config import settings


class TelegramDeliveryService:

    def __init__(self) -> None:
        self.base_url = (
            "https://api.telegram.org/bot"
            f"{settings.telegram_bot_token}"
        )

    async def send_text(
        self,
        telegram_user_id: int,
        text: str,
    ) -> dict[str, Any]:

        url = f"{self.base_url}/sendMessage"

        payload = {
            "chat_id": telegram_user_id,
            "text": text,
            "parse_mode": "HTML",
        }

        async with httpx.AsyncClient(
            timeout=20
        ) as client:
            response = await client.post(
                url,
                json=payload,
            )

        response.raise_for_status()

        data = response.json()

        if not data.get("ok"):
            raise RuntimeError(
                "Telegram delivery failed."
            )

        return data["result"]


telegram_delivery_service = (
    TelegramDeliveryService()
)