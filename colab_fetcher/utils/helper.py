import os
import time

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
