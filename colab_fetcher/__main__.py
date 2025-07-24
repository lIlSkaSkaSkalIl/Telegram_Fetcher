from colab_fetcher.utils.logger import logger
from colab_fetcher.utils.client import app
from colab_fetcher.handlers.handler import start_handler, tgupload_command, handle_file_upload, handle_cancel

if __name__ == "__main__":
    logger.info("Starting the bot...")
    app.run()
    logger.info("Bot stopped.")
