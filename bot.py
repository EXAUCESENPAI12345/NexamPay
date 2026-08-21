"""NexamPay Telegram bot.

Features:
- /start: sends the welcome message and mini-app link.
- /announce <message>: administrator-only broadcast to all registered users.

Run as a separate Render Worker/Background Worker so it does not block FastAPI.
"""
from __future__ import annotations

import asyncio
import html
import logging
from typing import Any

import httpx
from sqlalchemy import select

from app.config import settings
from app.database import AsyncSessionLocal
from app.models import User

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("nexampay.bot")

API = f"https://api.telegram.org/bot{settings.telegram_bot_token}"


async def telegram(method: str, **payload: Any) -> dict[str, Any]:
    async with httpx.AsyncClient(timeout=40) as client:
        response = await client.post(f"{API}/{method}", json=payload)
        response.raise_for_status()
        data = response.json()
        if not data.get("ok"):
            raise RuntimeError(data.get("description", "Telegram API error"))
        return data


async def send_message(chat_id: int, text: str, *, html_mode: bool = True) -> None:
    payload = {"chat_id": chat_id, "text": text, "disable_web_page_preview": True}
    if html_mode:
        payload["parse_mode"] = "HTML"
    await telegram("sendMessage", **payload)


async def send_welcome(chat_id: int) -> None:
    await send_message(
        chat_id,
        "👋 <b>Bienvenue sur NexamPay</b>\n\n"
        "Votre portefeuille numérique pour gérer vos opérations depuis Telegram.\n\n"
        "Ouvrez la Mini App pour commencer."
    )


async def broadcast(text: str) -> tuple[int, int]:
    sent = failed = 0
    async with AsyncSessionLocal() as db:
        result = await db.execute(select(User.telegram_id).where(User.is_active.is_(True)))
        telegram_ids = [int(x) for x in result.scalars().all()]

    for chat_id in telegram_ids:
        try:
            safe_text = html.escape(text)
            await send_message(chat_id, f"📢 <b>Annonce NexamPay</b>\n\n{safe_text}")
            sent += 1
        except Exception as exc:
            failed += 1
            logger.warning("Announcement failed for %s: %s", chat_id, exc)
        await asyncio.sleep(0.04)
    return sent, failed


async def handle_update(update: dict[str, Any]) -> None:
    message = update.get("message") or {}
    text = str(message.get("text") or "").strip()
    chat_id = (message.get("chat") or {}).get("id")
    from_user = message.get("from") or {}
    telegram_id = int(from_user.get("id") or 0)
    if not chat_id or not text:
        return

    command = text.split(maxsplit=1)[0].lower()
    if command == "/start" or command.startswith("/start@"):
        await send_welcome(int(chat_id))
        return

    if text.lower().startswith("/announce") or text.lower().startswith("/annonce"):
        if settings.admin_telegram_id is None or telegram_id != settings.admin_telegram_id:
            await send_message(int(chat_id), "⛔ Accès administrateur requis.")
            return
        parts = text.split(maxsplit=1)
        if len(parts) < 2 or not parts[1].strip():
            await send_message(int(chat_id), "Utilisation : <code>/announce Votre message</code>")
            return
        sent, failed = await broadcast(parts[1].strip())
        await send_message(int(chat_id), f"✅ Annonce envoyée.\nDestinataires : {sent}\nÉchecs : {failed}")


async def run() -> None:
    if not settings.telegram_bot_token:
        raise RuntimeError("TELEGRAM_BOT_TOKEN is required")
    offset: int | None = None
    logger.info("NexamPay bot started")
    while True:
        try:
            data = await telegram("getUpdates", timeout=30, offset=offset, allowed_updates=["message"])
            for update in data.get("result", []):
                offset = int(update["update_id"]) + 1
                try:
                    await handle_update(update)
                except Exception as exc:
                    logger.exception("Update handling failed: %s", exc)
        except Exception as exc:
            logger.exception("Polling error: %s", exc)
            await asyncio.sleep(5)


if __name__ == "__main__":
    asyncio.run(run())
