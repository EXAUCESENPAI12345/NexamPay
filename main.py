import os
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, ContextTypes, filters

TOKEN = os.getenv("BOT_TOKEN")

VERSION = "6.0.1"

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(f"NexamPay v{VERSION} 🚀\nBot en ligne")

async def handle(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(f"[v{VERSION}] Tu as dit: {update.message.text}")

def main():
    if not TOKEN:
        print("❌ TOKEN manquant")
        return

    app = Application.builder().token(TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle))

    print(f"NexamPay v{VERSION} démarré 🚀")
    app.run_polling(drop_pending_updates=True)

if __name__ == "__main__":
    main()
