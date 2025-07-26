import os
from datetime import datetime 
from typing import Optional
from pyrogram.types import Message
from pyrogram.enums import ParseMode
from humanize import naturalsize

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
    
def format_duration(seconds: float) -> str:
    minutes = int(seconds) // 60
    secs = int(seconds) % 60
    parts = []
    if minutes > 0:
        parts.append(f"{minutes}m")
    parts.append(f"{secs}s")
    return " ".join(parts)
    
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


def get_output_directory() -> str:
    drive_path = "/content/drive/MyDrive/Colab Fetcher"
    local_path = "/content/downloads"

    if os.path.exists("/content/drive") and os.path.ismount("/content/drive"):
        os.makedirs(drive_path, exist_ok=True)
        return drive_path
    else:
        os.makedirs(local_path, exist_ok=True)
        return local_path

