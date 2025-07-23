from colab_fetcher.bot.logger import logger
from colab_fetcher.bot.client import app
from colab_fetcher.handlers.handler import start_handler, download_command, handle_file_upload

if __name__ == "__main__":
    logger.info("Starting the bot...")
    app.run()
    logger.info("Bot stopped.")
