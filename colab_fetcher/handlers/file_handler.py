from pyrogram import Client, filters
from pyrogram.types import Message
from colab_fetcher.utils.user_state import get_user_state, clear_user_state
import os

@Client.on_message(filters.document | filters.video | filters.audio | filters.photo)
async def handle_file_upload(client: Client, message: Message):
    state = get_user_state(message.from_user.id)
    if state == "waiting_for_file":
        await message.reply_text("Downloading file...")
        file_path = await message.download(file_name=message.file_name or None)
        clear_user_state(message.from_user.id)

        if file_path and os.path.exists(file_path):
            await message.reply_text(f"✅ File downloaded successfully!\n\n📁 Saved to: `{file_path}`")
        else:
            await message.reply_text("❌ Failed to download the file.")
