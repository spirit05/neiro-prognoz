"""
Настройка логирования для модульной архитектуры
"""

import logging
import sys
from pathlib import Path
from config.paths import LOGS_DIR

def setup_logging(module_name: str, log_level: int = logging.INFO) -> logging.Logger:
    """
    Настройка логирования для модуля
    
    Args:
        module_name: Имя модуля для логирования
        log_level: Уровень логирования
    
    Returns:
        Настроенный логгер
    """
    logger = logging.getLogger(module_name)
    logger.setLevel(log_level)
    
    # Очищаем существующие обработчики
    for handler in logger.handlers[:]:
        logger.removeHandler(handler)
    
    # Форматтер
    formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    
    # Файловый обработчик
    log_file = LOGS_DIR / f"{module_name}.log"
    file_handler = logging.FileHandler(log_file, encoding='utf-8')
    file_handler.setFormatter(formatter)
    logger.addHandler(file_handler)
    
    # Консольный обработчик
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)
    
    return logger

# Специализированные логгеры для разных модулей
def get_ml_system_logger():
    """Логгер для ML системы"""
    return setup_logging("ml_system")

def get_auto_learning_logger():
    """Логгер для автообучения"""
    return setup_logging("auto_learning")

def get_telegram_bot_logger():
    """Логгер для Telegram бота"""
    return setup_logging("telegram_bot")

def get_web_interface_logger():
    """Логгер для веб-интерфейса"""
    return setup_logging("web_interface")

# Утилиты логирования
class ProgressLogger:
    """Класс для логирования прогресса с callback поддержкой"""
    
    def __init__(self, logger: logging.Logger, progress_callback=None):
        self.logger = logger
        self.progress_callback = progress_callback
    
    def info(self, message: str):
        """Информационное сообщение с callback"""
        self.logger.info(message)
        if self.progress_callback:
            self.progress_callback(message)
    
    def error(self, message: str):
        """Сообщение об ошибке с callback"""
        self.logger.error(message)
        if self.progress_callback:
            self.progress_callback(f"❌ {message}")
    
    def warning(self, message: str):
        """Предупреждение с callback"""
        self.logger.warning(message)
        if self.progress_callback:
            self.progress_callback(f"⚠️ {message}")
    
    def success(self, message: str):
        """Сообщение об успехе с callback"""
        self.logger.info(f"✅ {message}")
        if self.progress_callback:
            self.progress_callback(f"✅ {message}")