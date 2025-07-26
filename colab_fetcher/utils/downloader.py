import os
import time
import asyncio
from tqdm import tqdm
from humanize import naturalsize
from pyrogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton
from pyrogram.enums import ParseMode
from colab_fetcher.utils.helper import format_duration, get_progress_text

active_downloads = {}

async def download_with_progress(client, message: Message, file_path: str, output_dir: str):
    start_time = time.time()
    filename = os.path.basename(file_path)
    media_type = message.media.value.capitalize()
    progress_msg = None
    is_cancelled = False
    last_progress_text = None
    last_update = 0

    # Cancel button markup
    cancel_markup = InlineKeyboardMarkup([[
        InlineKeyboardButton("❌ Cancel", callback_data=f"cancel_dl_{message.id}")
    ]])

    active_downloads[message.id] = False  # Register download

    with tqdm(
        total=getattr(message.document, "file_size", 0),
        unit="B",
        unit_scale=True,
        unit_divisor=1024,
        miniters=1,
        desc=filename
    ) as pbar:

        async def progress(current, total):
            nonlocal progress_msg, is_cancelled, last_progress_text, last_update

            if active_downloads.get(message.id):
                is_cancelled = True
                if progress_msg:
                    try:
                        await progress_msg.edit_text("❌ Download cancelled by user", reply_markup=None)
                    except Exception as e:
                        pass  # Suppress cancellation display error
                return

            # Update tqdm
            pbar.update(current - pbar.n)

            # Calculate progress info
            elapsed = time.time() - start_time
            speed = current / elapsed if elapsed > 0 else 0
            eta = (total - current) / speed if speed > 0 else 0
            
            progress_text = get_progress_text(
                filename=filename,
                current=current,
                total=total,
                speed=speed,
                elapsed=elapsed,
                eta=eta,
                output_dir=output_dir
            )

            if (time.time() - last_update >= 5 or abs(percent - pbar.n / total * 100) >= 5):
                if progress_text != last_progress_text:
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
                        last_progress_text = progress_text
                        last_update = time.time()
                    except Exception as e:
                        pass  # Avoid crash if edit_text fails

        try:
            # Start download
            file_path = await message.download(
                file_name=file_path,
                progress=progress
            )

            # If cancelled
            if is_cancelled:
                try:
                    if file_path and os.path.exists(file_path):
                        os.remove(file_path)
                except Exception as e:
                    pass
                return None, None

            # Delete progress message on success
            if progress_msg:
                try:
                    await progress_msg.delete()
                except:
                    pass

            elapsed = time.time() - start_time
            return file_path, elapsed

        except Exception as e:
            if progress_msg and not is_cancelled:
                try:
                    await progress_msg.edit_text(f"⚠️ Download error: {str(e)}", reply_markup=None)
                except:
                    pass
            return None, None

        finally:
            active_downloads.pop(message.id, None)
