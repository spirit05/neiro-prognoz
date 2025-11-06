import logging
import os
import sys
from config.paths import paths

class ProjectLogger:
    _loggers = {}

    @classmethod
    def get_logger(cls, name, log_file=None, level=logging.INFO):
        if name in cls._loggers:
            return cls._loggers[name]
        logger = logging.getLogger(name)
        logger.setLevel(level)
        formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s', datefmt='%Y-%m-%d %H:%M:%S')
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setFormatter(formatter)
        logger.addHandler(console_handler)
        if log_file:
            os.makedirs(os.path.dirname(log_file), exist_ok=True)
            file_handler = logging.FileHandler(log_file, encoding='utf-8')
            file_handler.setFormatter(formatter)
            logger.addHandler(file_handler)
        cls._loggers[name] = logger
        return logger

def get_training_logger():
    return ProjectLogger.get_logger('Training', paths.TRAINING_LOG, logging.INFO)

def get_auto_learning_logger():
    return ProjectLogger.get_logger('Autolearning', paths.AUTO_LEARNING_LOG, logging.INFO)

def get_web_logger():
    return ProjectLogger.get_logger('WebInterface', paths.WEB_INTERFACE_LOG, logging.INFO)

def get_ml_system_logger():
    return ProjectLogger.get_logger('MLSystem', paths.ML_SYSTEM_LOG, logging.INFO)

def get_telegram_logger():
    return ProjectLogger.get_logger('TelegramBot', paths.TELEGRAM_BOT_LOG, logging.INFO)

def get_api_client_logger():
    return ProjectLogger.get_logger('APIClient', paths.API_CLIENT_LOG, logging.INFO)

def setup_all_loggers():
    loggers = [
        get_training_logger(),
        get_auto_learning_logger(),
        get_web_logger(),
        get_ml_system_logger(),
        get_telegram_logger(),
        get_api_client_logger(),
    ]
    for logger in loggers:
        logger.info(f"Логгер {logger.name} инициализирован")
    return loggers