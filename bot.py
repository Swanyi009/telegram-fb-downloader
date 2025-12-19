import os
import re
import asyncio
from telegram import Update
from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    MessageHandler,
    ContextTypes,
    filters,
)

TOKEN ="8347146318:AAFzx6jsz1e33nTg3mq4si9T-yZRcOGU-KY" 

FB_REGEX = r"(https?://)?(www\.)?(facebook\.com|fb\.watch)/.+"

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "👋 မင်္ဂလာပါ\n"
        "Facebook video link ကို ပို့လိုက်ပါ 📥"
    )

async def help_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "📌 အသုံးပြုနည်း\n"
        "Facebook video link ကို ပို့ပါ\n"
        "Bot က video ကို download လုပ်ပြီး ပြန်ပို့ပါမယ်"
    )

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text.strip()

    if not re.match(FB_REGEX, text):
        await update.message.reply_text("❌ Facebook link မဟုတ်ပါ")
        return

    await update.message.reply_text("⏳ Downloading... ခဏစောင့်ပါ")

    filename = "video.mp4"

    cmd = [
        "yt-dlp",
        "-f",
        "mp4",
        "-o",
        filename,
        text
    ]

    try:
        process = await asyncio.create_subprocess_exec(
            *cmd,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE,
        )
        await process.communicate()

        if not os.path.exists(filename):
            await update.message.reply_text("❌ Download မအောင်မြင်ပါ")
            return

        await update.message.reply_video(
            video=open(filename, "rb"),
            caption="✅ Download complete"
        )

    except Exception as e:
        await update.message.reply_text(f"Error: {e}")

    finally:
        if os.path.exists(filename):
            os.remove(filename)

def main():
    app = ApplicationBuilder().token(TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("help", help_cmd))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

    print("🚀 Facebook Downloader Bot is running...")
    app.run_polling()

if __name__ == "__main__":
    main()
import os
import subprocess
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes

TOKEN = os.getenv("TOKEN")

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "👋 မင်္ဂလာပါ\n"
        "Facebook video link ကို /fb နဲ့ပို့ပါ\n\n"
        "ဥပမာ:\n/fb https://www.facebook.com/xxxx"
    )

async def help_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "📌 အသုံးပြုနည်း\n"
        "/fb + Facebook video link"
    )

async def fb(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not context.args:
        await update.message.reply_text("Facebook video link ထည့်ပါ")
        return

    url = context.args[0]
    await update.message.reply_text("⏳ Downloading...")

    subprocess.run([
        "yt-dlp",
        "-f", "mp4",
        "-o", "video.mp4",
        url
    ])

    await update.message.reply_video(video=open("video.mp4", "rb"))

def main():
    app = ApplicationBuilder().token(TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("help", help_cmd))
    app.add_handler(CommandHandler("fb", fb))

    print("🚀 Facebook Downloader Bot is running...")
    app.run_polling()

if __name__ == "__main__":
    main()
