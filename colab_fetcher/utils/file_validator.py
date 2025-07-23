import os
from typing import Union
from pyrogram.types import Message

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
    """Validasi file yang diizinkan"""
    if message.document:
        file_name = message.document.file_name or ""
        return any(file_name.lower().endswith(ext) for ext in EXTENSIONS)
    return True  # Untuk photo/video tanpa filename
