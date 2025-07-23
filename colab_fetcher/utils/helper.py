import os
import time
from pyrogram.types import Message
from pyrogram.enums import ParseMode

def sanitize_filename(name: str) -> str:
    """Sanitize filename to remove unsupported characters."""
    return "".join(c for c in name if c.isalnum() or c in (' ', '.', '_')).rstrip()

def get_unique_filename(directory: str, filename: str = None, caption: str = None) -> str:
    """Generate a unique filename using filename, caption, or timestamp fallback."""
    # Prioritization: filename > caption > timestamp
    if filename:
        base = os.path.splitext(filename)[0]
        ext = os.path.splitext(filename)[1] or ""
    elif caption:
        base = sanitize_filename(caption)
        ext = ""
    else:
        base = str(int(time.time()))
        ext = ""

    candidate = f"{base}{ext}"
    counter = 1

    while os.path.exists(os.path.join(directory, candidate)):
        candidate = f"{base}_{counter}{ext}"
        counter += 1

    return candidate


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

