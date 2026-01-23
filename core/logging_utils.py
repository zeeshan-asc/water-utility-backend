"""
Logging utilities for AquaSentinel API
"""

import logging
import os
from pathlib import Path
from datetime import datetime

def setup_logging():
    """
    Setup comprehensive logging for the application.
    
    Returns:
        tuple: (api_logger, data_logger) - Logger instances
    """
    # Create logs directory if it doesn't exist
    logs_dir = Path(__file__).parent.parent / "logs"
    logs_dir.mkdir(exist_ok=True)
    
    # Configure API logger
    api_logger = logging.getLogger('aquasentinel.api')
    api_logger.setLevel(logging.INFO)
    
    # Remove existing handlers
    api_logger.handlers = []
    
    # File handler
    api_file_handler = logging.FileHandler(
        logs_dir / 'aquasentinel_api.log',
        encoding='utf-8'
    )
    api_file_handler.setLevel(logging.INFO)
    
    # Console handler
    api_console_handler = logging.StreamHandler()
    api_console_handler.setLevel(logging.INFO)
    
    # Formatter
    formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    
    api_file_handler.setFormatter(formatter)
    api_console_handler.setFormatter(formatter)
    
    api_logger.addHandler(api_file_handler)
    api_logger.addHandler(api_console_handler)
    
    # Configure data logger
    data_logger = logging.getLogger('aquasentinel.data')
    data_logger.setLevel(logging.INFO)
    data_logger.handlers = []
    
    data_file_handler = logging.FileHandler(
        logs_dir / 'aquasentinel_data.log',
        encoding='utf-8'
    )
    data_file_handler.setLevel(logging.INFO)
    data_file_handler.setFormatter(formatter)
    
    data_logger.addHandler(data_file_handler)
    data_logger.addHandler(api_console_handler)
    
    return api_logger, data_logger


