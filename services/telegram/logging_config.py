#/opt/model/services/telegram/logging_config.py
"""
Настройка логирования для Telegram бота
"""

import os
import sys
import logging
from pathlib import Path
from .config import TelegramConfig


def setup_telegram_logging(config: TelegramConfig = None) -> logging.Logger:
    """
    Настройка логирования для Telegram бота
    Возвращает корневой логгер для бота
    """
    if config is None:
        config = TelegramConfig()
    
    # Получаем настройки логирования
    log_level_name = config.get_log_level()
    log_file_path = config.get_log_file_path()
    
    # Преобразуем уровень логирования
    log_level = getattr(logging, log_level_name.upper(), logging.INFO)
    
    # Создаем директорию для логов если не существует
    log_file_path.parent.mkdir(parents=True, exist_ok=True)
    
    # Настраиваем формат логов
    formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    
    # Настраиваем обработчик для файла
    file_handler = logging.FileHandler(log_file_path, encoding='utf-8')
    file_handler.setLevel(log_level)
    file_handler.setFormatter(formatter)
    
    # Настраиваем обработчик для консоли
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(log_level)
    console_handler.setFormatter(formatter)
    
    # Настраиваем корневой логгер для telegram бота
    telegram_logger = logging.getLogger('telegram_bot')
    telegram_logger.setLevel(log_level)
    
    # Удаляем существующие обработчики (чтобы избежать дублирования)
    telegram_logger.handlers = []
    
    # Добавляем обработчики
    telegram_logger.addHandler(file_handler)
    telegram_logger.addHandler(console_handler)
    
    # Отключаем propagation для избежания дублирования в корневом логгере
    telegram_logger.propagate = False
    
    # Настраиваем логгеры для подмодулей
    for module in ['bot', 'config', 'security', 'ml_dispatcher', 'commands', 'handlers']:
        module_logger = logging.getLogger(f'telegram_bot.{module}')
        module_logger.setLevel(log_level)
        module_logger.propagate = False
    
    # Логируем информацию о настройке логирования
    telegram_logger.info(f"✅ Логирование настроено. Уровень: {log_level_name}")
    telegram_logger.info(f"📁 Логи будут сохраняться в: {log_file_path}")
    
    return telegram_logger


def get_telegram_logger(name: str = None) -> logging.Logger:
    """
    Получение логгера для Telegram бота
    Если name не указан, возвращает корневой логгер
    """
    if name is None:
        return logging.getLogger('telegram_bot')
    else:
        return logging.getLogger(f'telegram_bot.{name}')
