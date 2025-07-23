from pyrogram import Client, filters
from pyrogram.types import Message
from colab_fetcher.utils.user_state import set_user_state
from colab_fetcher.bot.logger import logger

@app.on_message(filters.command("download"))
async def download_command(client: Client, message: Message):
    try:
        logger.info(f"Received /download command from user {message.from_user.id}")
        await message.reply_text("Please send the file you want to download.")
        set_user_state(message.from_user.id, "waiting_for_file")
        logger.info(f"Set user {message.from_user.id} state to 'waiting_for_file'")
    except Exception as e:
        logger.error(f"Error in /download handler: {e}")
