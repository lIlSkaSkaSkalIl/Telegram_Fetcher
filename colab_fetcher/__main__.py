from pyrogram import Client
from utility.bot_handler import setup_handlers
from utility.config_manager import ConfigManager
from utility.helper import setup_logging

def main():
    logger = setup_logging()
    
    try:
        # Setup config
        config_manager = ConfigManager()
        config = config_manager.setup_config()
        
        # Initialize bot
        logger.info("Memulai Telegram Bot...")
        app = Client(
            "my_colab_bot",
            api_id=config["api_id"],
            api_hash=config["api_hash"],
            bot_token=config["bot_token"],
            plugins=dict(root="colab_fetcher")
        )
        
        setup_handlers(app)
        app.run()
        
    except Exception as e:
        logger.error(f"Bot gagal dijalankan: {e}", exc_info=True)
    finally:
        logger.info("Bot dihentikan")

if __name__ == "__main__":
    main()
