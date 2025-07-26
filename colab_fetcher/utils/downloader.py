import os
import time
import asyncio
from tqdm import tqdm
from pyrogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton
from pyrogram.enums import ParseMode
from collections import defaultdict

# Gunakan defaultdict untuk menghindari KeyError
active_downloads = defaultdict(bool)
download_tasks = {}

async def download_with_progress(client, message: Message, file_path: str, output_dir: str):
    start_time = time.time()
    filename = os.path.basename(file_path)
    progress_msg = None
    last_progress_text = None
    last_update = 0

    # Cancel button markup
    cancel_markup = InlineKeyboardMarkup([[
        InlineKeyboardButton("❌ Cancel", callback_data=f"cancel_dl_{message.id}")
    ]])

    # Register download
    active_downloads[message.id] = False
    current_task = asyncio.current_task()
    download_tasks[message.id] = current_task

    try:
        with tqdm(
            total=getattr(message.document, "file_size", 0),
            unit="B",
            unit_scale=True,
            unit_divisor=1024,
            miniters=1,
            desc=filename
        ) as pbar:

            async def progress(current, total):
                nonlocal progress_msg, last_progress_text, last_update

                # Check for cancellation
                if active_downloads[message.id]:
                    raise asyncio.CancelledError("Download cancelled by user")

                # Update progress bar
                pbar.update(current - pbar.n)

                # Throttle progress updates to every 5 seconds
                if time.time() - last_update >= 5:
                    progress_text = get_progress_text(
                        filename=filename,
                        current=current,
                        total=total,
                        speed=current / (time.time() - start_time) if (time.time() - start_time) > 0 else 0,
                        elapsed=time.time() - start_time,
                        eta=(total - current) * (time.time() - start_time) / current if current > 0 else 0,
                        output_dir=output_dir
                    )

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
                        except Exception:
                            pass

            try:
                # Start download
                file_path = await message.download(
                    file_name=file_path,
                    progress=progress
                )
                
                elapsed = time.time() - start_time
                return file_path, elapsed

            except asyncio.CancelledError:
                # Cleanup on cancellation
                if file_path and os.path.exists(file_path):
                    try:
                        os.remove(file_path)
                    except OSError:
                        pass
                
                if progress_msg:
                    try:
                        await progress_msg.edit_text("❌ Download cancelled", reply_markup=None)
                    except Exception:
                        pass
                
                return None, None

            except Exception as e:
                if progress_msg:
                    try:
                        await progress_msg.edit_text(f"⚠️ Download error: {str(e)}", reply_markup=None)
                    except Exception:
                        pass
                return None, None

            finally:
                # Cleanup progress message on success
                if progress_msg and not active_downloads[message.id]:
                    try:
                        await progress_msg.delete()
                    except Exception:
                        pass

    finally:
        # Cleanup state
        active_downloads.pop(message.id, None)
        download_tasks.pop(message.id, None)

