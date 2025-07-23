from colab_fetcher.bot.client import app
from colab_fetcher.bot import handlers
from colab_fetcher.bot.logger import logger

if __name__ == "__main__":
    logger.info("Starting the bot...")
    app.run()
    logger.info("Bot stopped.")
