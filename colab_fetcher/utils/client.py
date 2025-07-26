from pyrogram import Client
from colab_fetcher import load_credentials, logger

logger.info("Loading credentials...")
creds = load_credentials()
logger.info("Credentials loaded successfully.")

app = Client(
    "my_bot",
    api_id=creds["api_id"],
    api_hash=creds["api_hash"],
    bot_token=creds["bot_token"]
)

logger.info("Pyrogram client initialized.")
