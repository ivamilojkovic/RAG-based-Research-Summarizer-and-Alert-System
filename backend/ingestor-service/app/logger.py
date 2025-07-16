from loguru import logger
import sys

# Remove default logger to customize
logger.remove()

# Add console logging with pretty formatting
logger.add(sys.stdout, colorize=True, format="<green>{time:YYYY-MM-DD HH:mm:ss}</green> | <level>{level}</level> | <cyan>{message}</cyan>")
