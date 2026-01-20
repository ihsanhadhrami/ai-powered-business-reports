"""
Centralized Logging Configuration
Provides consistent logging across all modules.
"""

import logging
import os
from datetime import datetime
from pathlib import Path


def setup_logger(name: str, log_level: str = None) -> logging.Logger:
    """
    Create and configure a logger instance.
    
    Args:
        name: Logger name (usually __name__)
        log_level: Optional log level override (DEBUG, INFO, WARNING, ERROR)
    
    Returns:
        Configured logger instance
    """
    # Get log level from environment or use default
    level_str = log_level or os.getenv('LOG_LEVEL', 'INFO')
    level = getattr(logging, level_str.upper(), logging.INFO)
    
    # Create logger
    logger = logging.getLogger(name)
    logger.setLevel(level)
    
    # Avoid adding handlers multiple times
    if logger.handlers:
        return logger
    
    # Console handler with formatting
    console_handler = logging.StreamHandler()
    console_handler.setLevel(level)
    
    # Format: timestamp - level - module - message
    formatter = logging.Formatter(
        '%(asctime)s | %(levelname)-8s | %(name)s | %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)
    
    # Optional file handler
    log_to_file = os.getenv('LOG_TO_FILE', 'false').lower() == 'true'
    if log_to_file:
        log_dir = Path('logs')
        log_dir.mkdir(exist_ok=True)
        
        log_file = log_dir / f"app_{datetime.now().strftime('%Y%m%d')}.log"
        file_handler = logging.FileHandler(log_file, encoding='utf-8')
        file_handler.setLevel(level)
        file_handler.setFormatter(formatter)
        logger.addHandler(file_handler)
    
    return logger


# Create a default app logger
app_logger = setup_logger('email_report_app')
