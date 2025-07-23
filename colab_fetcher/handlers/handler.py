import os
from pyrogram import filters
from pyrogram.types import Message
from colab_fetcher.bot.client import app
from colab_fetcher.bot.logger import logger
from colab_fetcher.utils.user_state import set_user_state, get_user_state, clear_user_state

@app.on_message(filters.command("start") & filters.private)
async def start_handler(client, message: Message):
    user_id = message.from_user.id
    logger.info(f"/start command received from user {user_id}")
    
    await message.reply_text(
        "Hello! I'm your Telegram Fetcher bot.\n\n"
        "Send me a command and I'll assist you."
    )
    
    logger.info("Start message sent.")

@app.on_message(filters.command("download"))
async def download_command(client, message: Message):
    try:
        logger.info(f"Received /download command from user {message.from_user.id}")
        await message.reply_text("Please send the file you want to download.")
        set_user_state(message.from_user.id, "waiting_for_file")
        logger.info(f"Set user {message.from_user.id} state to 'waiting_for_file'")
    except Exception as e:
        logger.error(f"Error in /download handler: {e}")

@app.on_message(filters.document | filters.video | filters.audio | filters.photo)
async def handle_file_upload(client, message: Message):
    state = get_user_state(message.from_user.id)
    if state == "waiting_for_file":
        await message.reply_text("Downloading file...")
        file_path = await message.download(file_name=message.file_name or None)
        clear_user_state(message.from_user.id)

        if file_path and os.path.exists(file_path):
            await message.reply_text(f"✅ File downloaded successfully!\n\n📁 Saved to: `{file_path}`")
        else:
            await message.reply_text("❌ Failed to download the file.")
