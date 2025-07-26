import os
import time
import asyncio
import json

from tqdm import tqdm
from datetime import datetime 
from typing import Optional, Union
from humanize import naturalsize
from pyrogram import filters, Client
from pyrogram.enums import ParseMode
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton, Message
from pathlib import Path

from colab_fetcher import load_credentials
from colab_fetcher.utils.client import app

active_downloads = {}

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

def format_duration(seconds: float) -> str:
    minutes = int(seconds) // 60
    secs = int(seconds) % 60
    parts = []
    if minutes > 0:
        parts.append(f"{minutes}m")
    parts.append(f"{secs}s")
    return " ".join(parts)

def get_progress_text(filename, current, total, speed, elapsed, eta, output_dir):
    percent = current / total * 100
    filled = int(14 * percent / 100)
    bar = '█' * filled + '░' * (14 - filled)
                        
    return (
        f"<b>📥 Downloading...</b>\n\n"
        f"<b>{filename} »</b>\n\n"
        f"╭「{bar}」 {percent:.1f}%\n"
        f"├✅ <b>Downloaded:</b> {naturalsize(current)}\n"
        f"├📦 <b>Total Size:</b> {naturalsize(total)}\n"
        f"├⚡ <b>Speed:</b> {naturalsize(speed)}/s\n"
        f"├⏱️ <b>Elapsed:</b> {format_duration(elapsed)}\n"
        f"├⏳ <b>ETA:</b> {format_duration(eta)}\n"
        f"╰💾 <b>Saved To:</b> {output_dir}"
    )

async def download_with_progress(client, message: Message, file_path: str, output_dir: str):
    start_time = time.time()
    filename = os.path.basename(file_path)
    progress_msg = None
    is_cancelled = False
    last_progress_text = None
    last_update = 0

    # Cancel button
    cancel_markup = InlineKeyboardMarkup([[
        InlineKeyboardButton("❌ Cancel", callback_data=f"cancel_dl_{message.id}")
    ]])

    active_downloads[message.id] = False

    with tqdm(
        total = (
            getattr(message.document, "file_size", None) or
            getattr(message.video, "file_size", None) or
            getattr(message.audio, "file_size", None) or
            getattr(message.photo, "file_size", None) or
            0
        ),
        unit="B", unit_scale=True, unit_divisor=1024,
        miniters=1, desc=filename
    ) as pbar:

        async def progress(current, total):
            nonlocal progress_msg, is_cancelled, last_progress_text, last_update

            # Check cancel
            if active_downloads.get(message.id):
                is_cancelled = True
                raise asyncio.CancelledError()

            # Update TQDM
            pbar.update(current - pbar.n)

            elapsed = time.time() - start_time
            speed = current / elapsed if elapsed > 0 else 0
            eta = (total - current) / speed if speed > 0 else 0

            progress_text = get_progress_text(
                filename, current, total, speed, elapsed, eta, output_dir
            )

            if time.time() - last_update >= 5:
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
                return None, None

            if progress_msg:
                try:
                    await progress_msg.delete()
                except:
                    pass

            elapsed = time.time() - start_time
            return file_path, elapsed

        except asyncio.CancelledError:
            if progress_msg:
                try:
                    await progress_msg.edit_text("❌ Download cancelled by user", reply_markup=None)
                except:
                    pass
            if os.path.exists(file_path):
                os.remove(file_path)
            return None, None

        except Exception as e:
            if progress_msg:
                try:
                    await progress_msg.edit_text(f"⚠️ Download error: {str(e)}", reply_markup=None)
                except:
                    pass
            return None, None

        finally:
            active_downloads.pop(message.id, None)

def sanitize_filename(name: str) -> str:
    """Sanitize filename to remove unsupported characters."""
    return "".join(c for c in name if c.isalnum() or c in (' ', '.', '_')).rstrip()

def get_file_extension(message: Message) -> str:
    """Mendapatkan ekstensi file dari message"""
    if message.document:
        ext = os.path.splitext(message.document.file_name or "")[1]
    elif message.video:
        ext = os.path.splitext(message.video.file_name or "")[1] or ".mp4"
    elif message.audio:
        ext = os.path.splitext(message.audio.file_name or "")[1] or ".mp3"
    elif message.photo:
        ext = ".jpg"
    elif message.voice:
        ext = ".ogg"
    elif message.sticker:
        ext = ".webp"
    else:
        ext = ".bin"
    return ext.lower()

def get_start_message() -> str:
    return (
        "👋 <b>Hello!</b> I’m your <b>Telegram Fetcher</b> bot.\n\n"
        "📤 Send me a file or command and I’ll handle it.\n"
        "💾 Files will be saved to <b>local Colab storage</b>.\n\n"
        "☁️ To upload to <b>Google Drive</b>, make sure you’ve <i>mounted</i> it first.\n"
        "📁 Use available commands to begin uploading!"
    )

def get_tgupload_message() -> str:
    return (
        "📥 <b>Telegram File Upload</b>\n\n"
        "Please send the file you want to upload from Telegram.\n"
        "Make sure to send it as a <b>document</b> for best results.\n\n"
        "⏳ Waiting for your file..."
    )

def download_complete_message(file_path: str, unique_name: str, elapsed_time: float, output_dir: str) -> str:
    return (
        f"✅ <b>Download Complete!</b>\n\n"
        f"╭📂 <b>File Name »</b> <code>{unique_name}</code>\n"
        f"├📁 <b>Size »</b> {naturalsize(os.path.getsize(file_path))}\n"
        f"├⏱️ <b>Saved Time »</b> {format_duration(elapsed_time)}\n"
        f"╰💾 <b>Saved To »</b> {output_dir}"
    )

def get_unique_filename(directory: str, message: Message) -> str:
    """
    Generate unique filename dengan:
    1. Filename asli (jika ada) + ekstensi
    2. Caption (50 char) + ekstensi (jika tidak ada filename)
    3. Timestamp + ekstensi (fallback)
    """
    os.makedirs(directory, exist_ok=True)
    ext = get_file_extension(message)
    
    # Case 1: Filename asli
    if (message.document and message.document.file_name) or \
       (message.video and message.video.file_name) or \
       (message.audio and message.audio.file_name):
        filename = message.document.file_name if message.document else \
                  message.video.file_name if message.video else \
                  message.audio.file_name
        base = sanitize_filename(os.path.splitext(filename)[0])
        final_name = f"{base}{ext}"
    
    # Case 2: Caption
    elif message.caption:
        final_name = f"{sanitize_filename(message.caption)[:50]}{ext}"
    
    # Case 3: Timestamp
    else:
        final_name = f"{datetime.now().strftime('%Y%m%d%H%M%S')}{ext}"
    
    # Handle duplikat
    counter = 1
    original_name = final_name
    while os.path.exists(os.path.join(directory, final_name)):
        name_part, ext_part = os.path.splitext(original_name)
        final_name = f"{name_part}_{counter}{ext_part}"
        counter += 1
    
    return final_name

async def send_error(message: Message, error_type: str):
    """Mengirim pesan error yang user-friendly"""
    error_messages = {
        "invalid_type": (
            "❌ <b>File type not supported</b>\n"
            "Hanya menerima: Video, Audio, Gambar, PDF, atau Archive"
        ),
        "processing_error": "⚠️ <b>Terjadi error saat memproses file</b>",
        "download_failed": "⏳ <b>Gagal mengunduh file</b>\nCoba lagi nanti"
    }
    
    await message.reply_text(
        error_messages.get(error_type, "Terjadi kesalahan tidak diketahui"),
        parse_mode=ParseMode.HTML
    )

# Dictionary ekstensi file
EXTENSIONS = {
    # Video
    ".mp4": "video", ".avi": "video", ".mkv": "video", ".m2ts": "video",
    ".mov": "video", ".ts": "video", ".webm": "video", ".mpg": "video",
    # Audio
    ".mp3": "audio", ".wav": "audio", ".flac": "audio", ".aac": "audio",
    # Gambar
    ".jpg": "photo", ".jpeg": "photo", ".png": "photo", ".bmp": "photo",
    # Dokumen
    ".pdf": "pdf", ".doc": "document", ".docx": "document",
    # Archive
    ".zip": "archive", ".rar": "archive", ".7z": "archive",
    # Subtitle
    ".srt": "subtitle", ".ass": "subtitle"
}

def get_file_type(file_path: str) -> str:
    """Mendapatkan tipe file berdasarkan ekstensi"""
    _, ext = os.path.splitext(file_path)
    return EXTENSIONS.get(ext.lower(), "other")

def is_allowed_file(message: Message) -> bool:
    ext = get_file_extension(message)
    return ext in EXTENSIONS
    
def get_output_directory() -> str:
    drive_path = "/content/drive/MyDrive/Colab Fetcher"
    local_path = "/content/downloads"

    if os.path.exists("/content/drive") and os.path.ismount("/content/drive"):
        os.makedirs(drive_path, exist_ok=True)
        return drive_path
    else:
        os.makedirs(local_path, exist_ok=True)
        return local_path

STATE_FILE = Path(__file__).resolve().parent.parent / "config/user_state.json"
STATE_FILE.parent.mkdir(parents=True, exist_ok=True)

def load_user_state():
    if STATE_FILE.exists():
        with open(STATE_FILE, "r") as f:
            return json.load(f)
    return {}

def save_user_state(state_dict):
    with open(STATE_FILE, "w") as f:
        json.dump(state_dict, f, indent=4)

def set_user_state(user_id, state):
    state_dict = load_user_state()
    state_dict[str(user_id)] = state
    save_user_state(state_dict)

def get_user_state(user_id):
    return load_user_state().get(str(user_id), None)

def clear_user_state(user_id):
    state_dict = load_user_state()
    if str(user_id) in state_dict:
        del state_dict[str(user_id)]
        save_user_state(state_dict)


if __name__ == "__main__":
    logger.info("Starting the bot...")
    app.run()
    logger.info("Bot stopped.")
