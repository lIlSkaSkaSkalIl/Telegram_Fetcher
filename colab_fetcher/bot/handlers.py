from pyrogram import filters
from pyrogram.types import Message
from colab_fetcher.bot.client import app
from colab_fetcher.bot.logger import logger

@app.on_message(filters.command("start") & filters.private)
async def start_handler(client, message: Message):
    user_id = message.from_user.id
    logger.info(f"/start command received from user {user_id}")
    
    await message.reply_text(
        "Hello! I'm your Telegram Fetcher bot.\n\n"
        "Send me a command and I'll assist you."
    )
    
    logger.info("Start message sent.")
