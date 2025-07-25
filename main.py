#@title Telegram Fetcher
API_ID = 123 #@param {type:"number"}
API_HASH = "" #@param {type:"string"}
BOT_TOKEN = "" #@param {type:"string"}

import subprocess, json, shutil, os
from pathlib import Path
from IPython.display import clear_output

# ===== CONSTANTS =====
REPO_URL = "https://github.com/lIlSkaSkaSkalIl/Telegram_Fetcher"
REPO_DIR = "/content/Telegram_Fetcher"
CONFIG_DIR = f"{REPO_DIR}/colab_fetcher/config"

def log(msg, icon="🔧"):
    """Custom logger dengan emoji."""
    print(f"{icon} {msg}")

# Remove default Colab sample data
def remove_sample_data():
    if os.path.exists("/content/sample_data"):
        log("Removing /content/sample_data")
        shutil.rmtree("/content/sample_data")

def validate_inputs():
    """Validasi input API_ID, API_HASH, dan BOT_TOKEN."""
    if not all([API_ID, API_HASH, BOT_TOKEN]):
        raise ValueError("Semua field (API_ID, API_HASH, BOT_TOKEN) harus diisi!")
    try:
        int(API_ID)
    except ValueError:
        raise ValueError("API_ID harus berupa angka integer!")

def setup_repo():
    """Clone repository dari GitHub."""
    if os.path.exists(REPO_DIR):
        log("Menghapus repository lama...")
        shutil.rmtree(REPO_DIR)

    log("Cloning repository...")
    try:
        subprocess.run(["git", "clone", "--depth", "1", REPO_URL, REPO_DIR], check=True)
    except subprocess.CalledProcessError as e:
        raise RuntimeError(f"Gagal clone repo: {e}\nPastikan URL valid dan koneksi stabil.")

def install_deps():
    """Install dependencies dari requirements.txt."""
    req_path = f"{REPO_DIR}/requirements.txt"
    if not os.path.exists(req_path):
        raise FileNotFoundError(f"File {req_path} tidak ditemukan!")

    log("Menginstall dependencies...", icon="📦")
    process = subprocess.Popen(
        ["pip", "install", "-r", req_path],
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        text=True,
    )
    # Real-time output log
    for line in process.stdout:
        log(line.strip(), icon="🔹")
    if process.wait() != 0:
        raise RuntimeError("Instalasi gagal. Cek requirements.txt!")

def save_credentials():
    """Simpan credentials ke config/credentials.json."""
    os.makedirs(CONFIG_DIR, exist_ok=True)
    credentials = {
        "api_id": int(API_ID),
        "api_hash": API_HASH,
        "bot_token": BOT_TOKEN
    }
    try:
        with open(f"{CONFIG_DIR}/credentials.json", "w") as f:
            json.dump(credentials, f, indent=4)
        log("Credentials disimpan!", icon="🔑")
    except Exception as e:
        raise IOError(f"Gagal menyimpan credentials: {e}")

def run_bot():
    """Jalankan bot dari package colab_fetcher."""
    log("Memulai bot...", icon="🚀")
    try:
        !cd /content/Telegram_Fetcher/ && python3 -m colab_fetcher
    except subprocess.CalledProcessError as e:
        raise RuntimeError(f"Bot crash! Error: {e}")


try:
    remove_sample_data()
    validate_inputs()
    setup_repo()
    install_deps()
    save_credentials()
    clear_output()
    run_bot()
except Exception as e:
    log(f"ERROR: {str(e)}", icon="❌")
    raise
