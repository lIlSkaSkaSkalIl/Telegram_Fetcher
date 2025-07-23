import os
import time
import asyncio
from tqdm import tqdm
from humanize import naturalsize
from pyrogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton
from pyrogram.enums import ParseMode

# Untuk manajemen download aktif
active_downloads = {}

async def download_with_progress(client, message: Message, file_path: str):
    """Download file dengan progress bar + cancel button"""
    start_time = time.time()
    filename = os.path.basename(file_path)
    media_type = message.media.value.capitalize()
    progress_msg = None
    is_cancelled = False

    # Cancel button markup
    cancel_markup = InlineKeyboardMarkup([[
        InlineKeyboardButton("❌ Cancel", callback_data=f"cancel_dl_{message.id}")
    ]])

    # Registrasi download aktif
    active_downloads[message.id] = False

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
            nonlocal last_update, progress_msg, is_cancelled
            
            # Cek jika user membatalkan
            if active_downloads.get(message.id, False):
                is_cancelled = True
                raise Exception("Download dibatalkan oleh user")

            pbar.update(current - pbar.n)
            elapsed = time.time() - start_time
            speed = current / elapsed if elapsed > 0 else 0
            eta = (total - current) / speed if speed > 0 else 0
            
            # Format progress text
            percent = current / total * 100
            filled_length = int(14 * current // total)
            bar = "█" * filled_length + "░" * (14 - filled_length)
            
            progress_text = (
                f"<b>Downloading...\n\n</b>"
                f"<b>» {filename}</b>\n\n"
                f"╭「{bar}」<b>»</b> {percent:.1f}%\n"
                f"├📥 <b>Downloaded »</b> {naturalsize(current)}\n"
                f"├📁 <b>Total Size »</b> {naturalsize(total)}\n"
                f"├⚡ <b>Speed »</b> {naturalsize(speed)}/s\n"
                f"├📂 <b>File Type »</b> {media_type}\n"
                f"├⏱️ <b>Time Spent »</b> {time.strftime('%M:%S', time.gmtime(elapsed))}\n"
                f"╰⏳ <b>Time Left »</b> {time.strftime('%M:%S', time.gmtime(eta))}"
            )
            
            # Update setiap 5 detik atau 5% perubahan
            if time.time() - last_update >= 5 or percent - last_update >= 5:
                try:
                    if progress_msg:
                        await progress_msg.edit_text(
                            progress_text,
                            reply_markup=cancel_markup,
                            parse_mode=ParseMode.HTML
                        )
                    else:
                        progress_msg = await message.reply_text(
                            progress_text,
                            reply_markup=cancel_markup,
                            parse_mode=ParseMode.HTML
                        )
                    last_update = time.time()
                except:
                    pass

        try:
            file_path = await message.download(
                file_name=file_path,
                progress=progress
            )
            
            if is_cancelled:
                if os.path.exists(file_path):
                    os.remove(file_path)
                return None
                
            return file_path
            
        except Exception as e:
            if "batal" in str(e).lower():
                if progress_msg:
                    await progress_msg.edit_text("❌ Download dibatalkan oleh user")
            raise
        finally:
            if progress_msg:
                await progress_msg.edit_reply_markup(reply_markup=None)
            active_downloads.pop(message.id, None)
