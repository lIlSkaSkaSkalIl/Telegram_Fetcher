import logging
from pyrogram import filters
from pyrogram.types import Message

logger = logging.getLogger(__name__)

def setup_handlers(app):
    @app.on_message(filters.all)
    async def handle_all_messages(client, message: Message):
        try:
            log_message = (
                f"New message - ChatID: {message.chat.id} | "
                f"MsgID: {message.id} | "
                f"From: {message.from_user.id if message.from_user else 'N/A'} | "
                f"Content: {message.text or message.caption or 'Media content'}"
            )
            logger.info(log_message)
            
            await message.reply("Pesan diterima dan tercatat!")
            
        except Exception as e:
            logger.error(f"Error handling message: {e}", exc_info=True)
