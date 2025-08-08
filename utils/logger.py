"""
Logging configuration for PDF Summarizer
"""
import sys
import os
from loguru import logger

def setup_logging():
    """Configure logging for the application"""
    # Remove default handler
    logger.remove()
    
    # Add console handler with custom format
    logger.add(
        sys.stderr,
        format="<green>{time:YYYY-MM-DD HH:mm:ss}</green> | <level>{level: <8}</level> | <level>{message}</level>",
        level=os.getenv("LOG_LEVEL", "INFO")
    )
    
    # Add file handler for persistent logging
    log_dir = "logs"
    os.makedirs(log_dir, exist_ok=True)
    
    logger.add(
        os.path.join(log_dir, "pdf_summarizer.log"),
        rotation="10 MB",
        retention="7 days",
        format="{time:YYYY-MM-DD HH:mm:ss} | {level: <8} | {name}:{function}:{line} | {message}",
        level="DEBUG"
    )
    
    return logger