import logging
import sys
from logging.handlers import RotatingFileHandler
import os
from dotenv import load_dotenv

# Load .env at the very beginning
load_dotenv()


def setup_logger():
    # Create logs directory if not exists
    if not os.path.exists('logs'):
        os.makedirs('logs')

    logger = logging.getLogger('discord_music_bot')
    
    # Check for debug mode in .env
    debug_mode = os.getenv('DEBUG_MODE', 'False').lower() == 'true'
    level = logging.DEBUG if debug_mode else logging.INFO
    logger.setLevel(level)


    # Formatter
    formatter = logging.Formatter(
        '%(asctime)s | %(levelname)-8s | %(name)s | %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )

    # Console Handler
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setFormatter(formatter)

    # File Handler
    file_handler = RotatingFileHandler(
        'logs/bot.log', 
        maxBytes=5*1024*1024, 
        backupCount=5,
        encoding='utf-8'
    )
    file_handler.setFormatter(formatter)

    logger.addHandler(console_handler)
    logger.addHandler(file_handler)

    # Also capture discord library logs
    discord_logger = logging.getLogger('discord')
    discord_logger.setLevel(level)
    discord_logger.addHandler(console_handler)
    discord_logger.addHandler(file_handler)

    return logger

log = setup_logger()
