# utils/logging_system.py
"""
Единая система логирования для всего проекта
"""

import logging
import os
import sys
from datetime import datetime
from config.paths import paths

class ProjectLogger:
    """Универсальный логгер для всех компонентов проекта"""
    
    _loggers = {}
    
    @classmethod
    def get_logger(cls, name, log_file=None, level=logging.INFO):
        """Получение или создание логгера"""
        if name in cls._loggers:
            return cls._loggers[name]
        
        # Создаем новый логгер
        logger = logging.getLogger(name)
        logger.setLevel(level)
        
        # Форматтер
        formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        )
        
        # Обработчик для консоли
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setFormatter(formatter)
        logger.addHandler(console_handler)
        
        # Обработчик для файла (если указан)
        if log_file:
            # Создаем директорию если не существует
            os.makedirs(os.path.dirname(log_file), exist_ok=True)
            
            file_handler = logging.FileHandler(log_file, encoding='utf-8')
            file_handler.setFormatter(formatter)
            logger.addHandler(file_handler)
        
        cls._loggers[name] = logger
        return logger

# Специализированные логгеры для разных компонентов
def get_training_logger():
    """Логгер для обучения ML модели"""
    return ProjectLogger.get_logger(
        'Training', 
        paths.TRAINING_LOG,
        logging.INFO
    )

def get_auto_learning_logger():
    """Логгер для автосервиса"""
    return ProjectLogger.get_logger(
        'AutoLearning', 
        paths.AUTO_LEARNING_LOG,
        logging.INFO
    )

def get_web_logger():
    """Логгер для веб-интерфейса"""
    return ProjectLogger.get_logger(
        'WebInterface', 
        paths.WEB_INTERFACE_LOG,
        logging.INFO
    )

def get_ml_system_logger():
    """Логгер для ML системы"""
    return ProjectLogger.get_logger(
        'MLSystem', 
        paths.ML_SYSTEM_LOG,
        logging.INFO
    )

def get_telegram_logger():
    """Логгер для Telegram бота"""
    return ProjectLogger.get_logger(
        'TelegramBot', 
        paths.TELEGRAM_BOT_LOG,
        logging.INFO
    )

def get_api_client_logger():
    """Логгер для API клиента"""
    return ProjectLogger.get_logger(
        'APIClient', 
        paths.API_CLIENT_LOG,
        logging.INFO
    )

def setup_all_loggers():
    """Настройка всех логгеров проекта"""
    loggers = [
        get_training_logger(),
        get_auto_learning_logger(), 
        get_web_logger(),
        get_ml_system_logger(),
        get_telegram_logger(),
        get_api_client_logger()
    ]
    
    # Логируем запуск системы логирования
    for logger in loggers:
        logger.info(f"🚀 Логгер {logger.name} инициализирован")
    
    return loggers