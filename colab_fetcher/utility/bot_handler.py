from pyrogram import filters
from pyrogram.types import Message
from .helper import setup_logging

logger = setup_logging()  # Inisialisasi logger

START_TEXT = """
🤖 **Bot Telegram Fetcher** 🤖

Halo! Saya adalah bot yang dibuat khusus untuk:
- Menyimpan pesan dari channel/group
- Bekerja di Google Colab
- Open source

Kirim /help untuk melihat petunjuk penggunaan.
"""

def setup_handlers(app):
    # Handler untuk command /start
    @app.on_message(filters.command("start"))
    async def start_command(client, message: Message):
        try:
            await message.reply_text(
                START_TEXT,
                disable_web_page_preview=True
            )
            logger.info(f"User {message.from_user.id} memulai bot")
        except Exception as e:
            logger.error(f"Error di /start: {e}", exc_info=True)
