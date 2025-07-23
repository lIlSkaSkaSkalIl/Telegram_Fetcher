from pyrogram import filters
from colab_fetcher.bot.client import app
from colab_fetcher.bot.logger import logger

@app.on_message(filters.private & filters.text)
async def echo(client, message):
    logger.info(f"Message received from user {message.from_user.id}: {message.text}")
    await message.reply_text(f"You said: {message.text}")
    logger.info("Reply sent.")
