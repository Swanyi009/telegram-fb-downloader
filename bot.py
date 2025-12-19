import os
import asyncio
import yt_dlp
from telegram import Update
from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    ContextTypes,
    MessageHandler,
    filters,
)

# Token from BotFather
TOKEN = os.getenv("TOKEN")

# Telegram max upload size for bots
MAX_SIZE = 50 * 1024 * 1024  # 50 MB

# Facebook URL pattern
FB_REGEX = r"(https?://)?(www\.)?(facebook\.com|fb\.watch)/.*"

# -------------------- Helper Functions --------------------
def split_file(file_path):
    """Split file into chunks if bigger than MAX_SIZE"""
    size = os.path.getsize(file_path)
    if size <= MAX_SIZE:
        return [file_path]
    chunks = []
    with open(file_path, "rb") as f:
        index = 1
        while True:
            chunk = f.read(MAX_SIZE)
            if not chunk:
                break
            chunk_name = f"{file_path}.part{index}"
            with open(chunk_name, "wb") as c:
                c.write(chunk)
            chunks.append(chunk_name)
            index += 1
    return chunks

async def download_video(url: str):
    """Download Facebook video with yt-dlp at best quality"""
    os.makedirs("downloads", exist_ok=True)
    ydl_opts = {
        "format": "best",
        "outtmpl": "downloads/%(title)s.%(ext)s",
        "quiet": True,
        "noplaylist": True,
    }
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        info = ydl.extract_info(url, download=True)
        file_path = ydl.prepare_filename(info)
    return file_path

# -------------------- Bot Handlers --------------------
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "👋 မင်္ဂလာပါ\n"
        "Facebook video link ကို ပို့လိုက်ပါ 📥"
        "Example: /fb <link>"
    )

async def help_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "📌 အသုံးပြုနည်း\n"
        "/start - Bot start message\n"
        "/help - Usage guide\n"
        "/fb <Facebook link> - Download video"
    )

async def fb(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if len(context.args) == 0:
        await update.message.reply_text("❌ Facebook link မပေးထားပါ။ Example: /fb <link>")
        return
    url = context.args[0]
    if not re.match(FB_REGEX, url):
        await update.message.reply_text("❌ Valid Facebook URL မဟုတ်ပါ")
        return

    msg = await update.message.reply_text("⏳ Downloading video...")
    try:
        file_path = await asyncio.to_thread(download_video, url)
        # Split if bigger than MAX_SIZE
        files_to_send = split_file(file_path)
        for f in files_to_send:
            await context.bot.send_video(chat_id=update.effective_chat.id, video=open(f, "rb"))
        await msg.edit_text("✅ Video download complete!")
    except Exception as e:
        await msg.edit_text(f"❌ Error: {str(e)}")

# -------------------- Main --------------------
def main():
    app = ApplicationBuilder().token(TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("help", help_cmd))
    app.add_handler(CommandHandler("fb", fb))

    print("🚀 Facebook Downloader Bot is running...")
    app.run_polling()

if __name__ == "__main__":
    main()
