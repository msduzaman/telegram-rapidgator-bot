import os
import ftplib
import requests
from telegram import Update
from telegram.ext import ApplicationBuilder, MessageHandler, CommandHandler, ContextTypes, filters

TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
ALLOWED_USER_ID = int(os.getenv("ALLOWED_USER_ID", "0"))

RG_FTP_HOST = os.getenv("RG_FTP_HOST")
RG_FTP_USER = os.getenv("RG_FTP_USER")
RG_FTP_PASS = os.getenv("RG_FTP_PASSWORD")

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "Send a file and I will upload it directly to Rapidgator (cloud)."
    )

async def handle_file(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.message.from_user

    if user.id != ALLOWED_USER_ID:
        await update.message.reply_text("❌ You are not allowed to use this bot.")
        return

    file = update.message.document or update.message.video or update.message.audio
    if not file:
        await update.message.reply_text("Send a file, not a message.")
        return

    file_id = file.file_id
    tg_file = await context.bot.get_file(file_id)
    file_url = tg_file.file_path
    filename = file.file_name

    await update.message.reply_text("Uploading to Rapidgator… ⏳")

    try:
        ftp = ftplib.FTP()
        ftp.connect(RG_FTP_HOST)
        ftp.login(RG_FTP_USER, RG_FTP_PASS)
        ftp.set_pasv(True)

        response = requests.get(file_url, stream=True)
        ftp.storbinary(f"STOR {filename}", response.raw)
        ftp.quit()

        link = f"https://rapidgator.net/file/{filename}"
        await update.message.reply_text(f"✅ Uploaded!\n{link}")

    except Exception as e:
        await update.message.reply_text(f"❌ Upload failed: {e}")

def main():
    app = ApplicationBuilder().token(TELEGRAM_TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.ALL & ~filters.COMMAND, handle_file))
    app.run_polling()

if __name__ == "__main__":
    main()
