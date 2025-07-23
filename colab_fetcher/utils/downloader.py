import os
import time
import asyncio
from tqdm import tqdm
from humanize import naturalsize
from pyrogram.types import Message
from pyrogram.enums import ParseMode

async def download_with_progress(client, message: Message, file_path: str):
    """Download file dengan progress bar custom"""
    start_time = time.time()
    filename = getattr(message.document, "file_name", "Unknown")
    media_type = message.media.value.capitalize()
    progress_msg = None
    
    with tqdm(
        total=getattr(message.document, "file_size", 0),
        unit="B",
        unit_scale=True,
        unit_divisor=1024,
        miniters=1,
        desc=filename
    ) as pbar:
        last_update = 0
        
        async def progress(current, total):
            nonlocal last_update, progress_msg
            
            pbar.update(current - pbar.n)
            elapsed = time.time() - start_time
            speed = current / elapsed if elapsed > 0 else 0
            eta = (total - current) / speed if speed > 0 else 0
            
            # Format progress
            percent = current / total * 100
            filled_length = int(14 * current // total)
            bar = "█" * filled_length + "░" * (14 - filled_length)
            
            progress_text = (
                f"<b>Downloading...\n\n</b>"
                f"<b>» {filename}</b>\n\n"
                f"╭「{bar}」<b>»</b>{percent:.1f}%\n"
                f"├📥 <b>Downloaded »</b> {naturalsize(current)}\n"
                f"├📁 <b>Total Size »</b> {naturalsize(total)}\n"
                f"├⚡ <b>Speed »</b> {naturalsize(speed)}/s\n"
                f"├📂 <b>File Type »</b> {media_type}\n"
                f"├⏱️ <b>Time Spent »</b> {time.strftime('%M:%S', time.gmtime(elapsed))}\n"
                f"╰⏳ <b>Time Left »</b> {time.strftime('%M:%S', time.gmtime(eta))}"
            )
            
            if time.time() - last_update >= 5 or percent - last_update >= 5:
                if progress_msg:
                    await progress_msg.edit_text(progress_text, parse_mode=ParseMode.HTML)
                else:
                    progress_msg = await message.reply_text(progress_text, parse_mode=ParseMode.HTML)
                last_update = time.time()
        
        file_path = await message.download(file_name=file_path, progress=progress)
        if progress_msg:
            await progress_msg.delete()
            
    return file_path

