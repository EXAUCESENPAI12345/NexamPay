import os
import asyncio
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, ContextTypes, filters

TOKEN = os.getenv("BOT_TOKEN")
VERSION = "6.0.1"

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(f"NexamPay v{VERSION} 🚀 OK")

async def handle(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(update.message.text)

async def run_bot():
    if not TOKEN:
        print("❌ TOKEN manquant")
        return

    app = Application.builder().token(TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle))

    print("Bot lancé 🚀")

    await app.run_polling(drop_pending_updates=True)

if __name__ == "__main__":
    asyncio.run(run_bot())
