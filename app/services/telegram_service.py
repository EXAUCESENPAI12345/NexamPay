from typing import Any

import httpx

from app.config import settings


class TelegramService:

    def __init__(self) -> None:
        self.base_url = (
            "https://api.telegram.org/bot"
            f"{settings.telegram_bot_token}"
        )

    async def send_message(
        self,
        telegram_id: int,
        text: str,
    ) -> dict[str, Any]:

        url = f"{self.base_url}/sendMessage"

        payload = {
            "chat_id": telegram_id,
            "text": text,
            "parse_mode": "HTML",
            "disable_web_page_preview": True,
        }

        async with httpx.AsyncClient(
            timeout=15.0
        ) as client:
            response = await client.post(
                url,
                json=payload,
            )

        response.raise_for_status()

        data = response.json()

        if not data.get("ok"):
            raise RuntimeError(
                "Telegram API request failed."
            )

        return data


telegram_service = TelegramService()