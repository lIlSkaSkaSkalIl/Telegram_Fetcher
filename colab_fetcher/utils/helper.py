import os
from datetime import datetime 
from typing import Optional
from pyrogram.types import Message
from pyrogram.enums import ParseMode

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
        "👋 Hello! I'm your **Telegram Fetcher** bot.\n\n"
        "📥 Send me a file, or command and I'll handle it for you.\n"
        "💾 By default, files will be saved to the **local Colab storage**.\n\n"
        "☁️ If you want to upload to **Google Drive**, please make sure to *mount* your drive first.\n"
        "📂 Use the available commands to start uploading."
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
