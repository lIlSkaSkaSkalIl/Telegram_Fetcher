import os
from pyrogram import filters
from humanize import naturalsize
from pyrogram.types import Message
from pyrogram.enums import ParseMode
from colab_fetcher.utils.client import app
from colab_fetcher.utils.logger import logger
from colab_fetcher.utils.user_state import set_user_state, get_user_state, clear_user_state
from colab_fetcher.utils.helper import get_unique_filename
from colab_fetcher.utils.downloader import download_with_progress
from colab_fetcher.utils.file_validator import is_allowed_file
from colab_fetcher.utils.helper import send_error


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
        try:
            # Validasi file
            if not is_allowed_file(message):
                await send_error(message, "invalid_type")
                return

            # Setup directory
            output_dir = "/content/downloads"
            os.makedirs(output_dir, exist_ok=True)
            
            # Generate unique filename
            filename = message.document.file_name if message.document else None
            caption = message.caption
            unique_name = get_unique_filename(output_dir, filename, caption)
            file_path = os.path.join(output_dir, unique_name)
            
            # Download dengan progress
            downloaded_path = await download_with_progress(client, message, file_path)
            clear_user_state(message.from_user.id)
            
            if downloaded_path and os.path.exists(downloaded_path):
                await message.reply_text(
                    f"✅ <b>Download Complete!</b>\n\n"
                    f"📁 <b>Path:</b> <code>{downloaded_path}</code>\n"
                    f"📦 <b>Size:</b> {naturalsize(os.path.getsize(downloaded_path))}",
                    parse_mode=ParseMode.HTML
                )
            else:
                await send_error(message, "download_failed")
                
        except Exception as e:
            logger.error(f"Download error: {e}")
            await send_error(message, "processing_error")
            raise
        finally:
            clear_user_state(message.from_user.id)

