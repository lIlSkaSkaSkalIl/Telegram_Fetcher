from pyrogram import Client, filters
from pyrogram.types import Message
from colab_fetcher.utils.user_state import set_user_state

@Client.on_message(filters.command("download"))
async def download_command(client: Client, message: Message):
    await message.reply_text("Please send the file you want to download.")
    set_user_state(message.from_user.id, "waiting_for_file")
