import logging
from pathlib import Path

def setup_logging():
    """Setup custom logging configuration"""
    log_format = '%(name)s - %(levelname)s - %(message)s'
    
    # Create logs directory if not exists
    logs_dir = Path("logs")
    logs_dir.mkdir(exist_ok=True)
    
    logging.basicConfig(
        level=logging.INFO,
        format=log_format,
        handlers=[
            logging.FileHandler(logs_dir/'telegram_bot.log'),
            logging.StreamHandler()
        ]
    )
    
    return logging.getLogger(__name__)
