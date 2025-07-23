from colab_fetcher.bot.logger import logger
from colab_fetcher.bot.client import app
from colab_fetcher.handlers.start_handler import start_handler
from colab_fetcher.handlers.download_handler import download_command
from colab_fetcher.handlers.file_handler import handle_file_upload

if __name__ == "__main__":
    logger.info("Starting the bot...")
    app.run()
    logger.info("Bot stopped.")
