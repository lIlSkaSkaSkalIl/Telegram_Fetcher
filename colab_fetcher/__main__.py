import os
from humanize import naturalsize
from pyrogram import filters
from pyrogram.types import Message
from pyrogram.enums import ParseMode

from colab_fetcher.utils.logger import logger
from colab_fetcher.utils.client import app
from colab_fetcher.utils.user_state import set_user_state, get_user_state, clear_user_state
from colab_fetcher.utils.helper import get_unique_filename, get_start_message, get_tgupload_message, send_error, download_complete_message, get_output_directory
from colab_fetcher.utils.downloader import download_with_progress, active_downloads
from colab_fetcher.utils.file_validator import is_allowed_file

@app.on_message(filters.command("start") & filters.private)
async def start_handler(client, message: Message):
    user_id = message.from_user.id
    logger.info(f"/start command received from user {user_id}")
    await client.send_message(
        chat_id=message.chat.id,
        text=get_start_message(),
        reply_to_message_id=message.id
    )
    logger.info("Start message sent.")

@app.on_message(filters.command("tgupload"))
async def tgupload_command(client, message: Message):
    try:
        logger.info(f"Received /tgupload command from user {message.from_user.id}")

        await client.send_message(
            chat_id=message.chat.id,
            text=get_tgupload_message(),
            reply_to_message_id=message.id
        )

        set_user_state(message.from_user.id, "waiting_for_file")
        logger.info(f"Set user {message.from_user.id} state to 'waiting_for_file'")
    except Exception as e:
        logger.error(f"Error in /tgupload handler: {e}")

@app.on_message(filters.document | filters.video | filters.audio | filters.photo)
async def handle_file_upload(client, message: Message):
    try:
        output_dir = get_output_directory() 
        unique_name = get_unique_filename(output_dir, message)
        file_path = os.path.join(output_dir, unique_name)

        downloaded_path, elapsed_time = await download_with_progress(client, message, file_path, output_dir)

        if not downloaded_path:
            return

        complete_message = download_complete_message(downloaded_path, unique_name, elapsed_time, output_dir) 
        await client.send_message(
            chat_id=message.chat.id,
            text=complete_message,
            reply_to_message_id=message.id,
            parse_mode=ParseMode.HTML
        )
    except Exception as e:
        await send_error(message, "download_failed")
        logger.error(f"Download error: {e}")
    finally:
        clear_user_state(message.from_user.id)

@app.on_callback_query(filters.regex(r"cancel_dl_(\d+)"))
async def handle_cancel(client, callback_query):
    message_id = int(callback_query.data.split("_")[-1])

    if message_id in active_downloads:
        active_downloads[message_id] = True
        await callback_query.answer("Cancelling download...")
    else:
        await callback_query.answer("No active download to cancel", show_alert=True)


if __name__ == "__main__":
    logger.info("Starting the bot...")
    app.run()
    logger.info("Bot stopped.")
