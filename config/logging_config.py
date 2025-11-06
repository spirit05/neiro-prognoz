# config/logging_config.py
import logging
import os

def setup_logging(name, log_file=None, level=logging.INFO):
    """Простая настройка логирования"""
    logger = logging.getLogger(name)
    logger.setLevel(level)
    
    # Форматтер
    formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    # Хендлер для консоли
    console_handler = logging.StreamHandler()
    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)
    
    return logger

def get_logger(name):
    """Быстрое получение логгера"""
    return logging.getLogger(name)

setup_logger = setup_logging