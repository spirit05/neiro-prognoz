# services/telegram/config.py
"""
Конфигурация Telegram бота
"""

import json
import logging
from typing import Dict, Any
from config.paths import TELEGRAM_CONFIG_FILE

logger = logging.getLogger('telegram_bot')

class TelegramConfig:
    """Класс управления конфигурацией Telegram бота"""
    
    def __init__(self):
        self.config_path = TELEGRAM_CONFIG_FILE
        self.config = self._load_config()
    
    def _load_config(self) -> Dict[str, Any]:
        """Загрузка конфигурации из файла"""
        try:
            with open(self.config_path, 'r', encoding='utf-8') as f:
                config = json.load(f)
            logger.info("✅ Конфигурация Telegram бота загружена")
            return config
        except FileNotFoundError:
            logger.error(f"❌ Файл конфигурации не найден: {self.config_path}")
            return self._create_default_config()
        except Exception as e:
            logger.error(f"❌ Ошибка загрузки конфигурации: {e}")
            return self._create_default_config()
    
    def _create_default_config(self) -> Dict[str, Any]:
        """Создание конфигурации по умолчанию"""
        default_config = {
            "enabled": False,
            "bot_token": "",
            "chat_id": "",
            "notifications": {
                "critical_errors": True,
                "all_errors": True,
                "service_stop": True,
                "predictions": False,
                "status_command": True
            }
        }
        
        try:
            with open(self.config_path, 'w', encoding='utf-8') as f:
                json.dump(default_config, f, ensure_ascii=False, indent=2)
            logger.info(f"✅ Создана конфигурация по умолчанию: {self.config_path}")
        except Exception as e:
            logger.error(f"❌ Ошибка создания конфигурации по умолчанию: {e}")
        
        return default_config
    
    def save_config(self) -> bool:
        """Сохранение конфигурации в файл"""
        try:
            with open(self.config_path, 'w', encoding='utf-8') as f:
                json.dump(self.config, f, ensure_ascii=False, indent=2)
            logger.info("✅ Конфигурация Telegram бота сохранена")
            return True
        except Exception as e:
            logger.error(f"❌ Ошибка сохранения конфигурации: {e}")
            return False
    
    def get_bot_token(self) -> str:
        """Получение bot token"""
        return self.config.get('bot_token', '')
    
    def is_enabled(self) -> bool:
        """Проверка включен ли бот"""
        return self.config.get('enabled', False)
    
    def get_chat_id(self) -> str:
        """Получение chat_id"""
        return self.config.get('chat_id', '')
    
    def get_notification_settings(self) -> Dict[str, bool]:
        """Получение настроек уведомлений"""
        return self.config.get('notifications', {})
    
    def update_notification_setting(self, key: str, value: bool) -> bool:
        """Обновление настройки уведомлений"""
        if 'notifications' not in self.config:
            self.config['notifications'] = {}
        
        self.config['notifications'][key] = value
        return self.save_config()
    
    def validate_config(self) -> bool:
        """Валидация конфигурации"""
        if not self.is_enabled():
            return True  # Бот отключен - конфиг валиден
        
        if not self.get_bot_token():
            logger.error("❌ Bot token не указан в конфигурации")
            return False
        
        if not self.get_chat_id():
            logger.error("❌ Chat ID не указан в конфигурации")
            return False
        
        return True
