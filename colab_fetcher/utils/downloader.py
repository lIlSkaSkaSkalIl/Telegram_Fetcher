import os
import time
import asyncio
from tqdm import tqdm
from humanize import naturalsize
from pyrogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton
from pyrogram.enums import ParseMode
from colab_fetcher.utils.helper import format_duration

# Track active downloads
active_downloads = {}

async def download_with_progress(client, message: Message, file_path: str, output_dir: str):
    """Enhanced downloader with progress bar and cancellation"""
    start_time = time.time()
    filename = os.path.basename(file_path)
    media_type = message.media.value.capitalize()
    progress_msg = None
    is_cancelled = False

    # Setup cancel button
    cancel_markup = InlineKeyboardMarkup([[
        InlineKeyboardButton("❌ Cancel", callback_data=f"cancel_dl_{message.id}")
    ]])

    # Register active download
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
            
            # Check for cancellation
            if active_downloads.get(message.id, False):
                is_cancelled = True
                if progress_msg:
                    await progress_msg.edit_text(
                        "❌ Download cancelled by user",
                        reply_markup=None
                    )
                return False  # Stop download gracefully

            # Update progress bar
            pbar.update(current - pbar.n)
            
            # Calculate metrics
            elapsed = time.time() - start_time
            speed = current / elapsed if elapsed > 0 else 0
            eta = (total - current) / speed if speed > 0 else 0
            percent = current / total * 100
            
            # Format progress message
            filled = int(14 * percent / 100)
            progress_text = (
                f"<b>Downloading...</b>\n\n"
                f"<b>{filename} »</b>\n\n"
                f"╭「{'█' * filled}{'░' * (14 - filled)}」 {percent:.1f}%\n"
                f"├📥 <b>Downloaded »</b> {naturalsize(current)}\n"
                f"├📁 <b>Total Size »</b> {naturalsize(total)}\n"
                f"├⚡ <b>Speed »</b> {naturalsize(speed)}/s\n"
                f"├⏱️ <b>Elapsed »</b> {format_duration(elapsed)}\n"
                f"├⏳ <b>ETA »</b> {format_duration(eta)}\n"
                f"╰💾 <b>Saved To »</b> {output_dir}"
            )

            # Update message max every 5 seconds or 5% progress
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
            return True

        try:
            # Start download
            file_path = await message.download(
                file_name=file_path,
                progress=progress
            )
            
            # Handle cancellation
            if is_cancelled:
                if os.path.exists(file_path):
                    os.remove(file_path)
                if progress_msg:
                    await progress_msg.edit_text(
                        "❌ Download cancelled by user",
                        reply_markup=None
                    )
                return None, None

            # Download completed successfully
            if progress_msg:
                await progress_msg.delete()

            elapsed = time.time() - start_time
            return file_path, elapsed

        except Exception as e:
            if progress_msg and not is_cancelled:
                await progress_msg.edit_text(
                    f"⚠️ Download error: {str(e)}",
                    reply_markup=None
                )
            return None, None
            
        finally:
            # Cleanup
            active_downloads.pop(message.id, None)
