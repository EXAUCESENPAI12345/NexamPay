import os
import asyncio
from flask import Flask, request
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes

TOKEN = os.environ.get("BOT_TOKEN") # Lit le token de Render
URL = "https://nexampay.onrender.com" # Ton URL Render ici

app = Flask(__name__)
application = ApplicationBuilder().token(TOKEN).build()

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Bot déployé ✅")

application.add_handler(CommandHandler("start", start))

@app.post(f"/webhook/{TOKEN}")
async def webhook():
    update = Update.de_json(request.get_json(force=True), application.bot)
    await application.process_update(update)
    return "ok"

@app.get("/")
def home():
    return "Bot is alive"

if __name__ == "__main__":
    # Active le webhook au démarrage
    asyncio.run(application.bot.set_webhook(url=f"{URL}/webhook/{TOKEN}"))
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 10000)))
