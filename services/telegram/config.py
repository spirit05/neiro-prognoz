#/opt/model/services/telegram/config.py
"""
Конфигурация Telegram бота для новой ML системы
"""

import os
import yaml
import logging
from typing import Dict, Any, Optional
from pathlib import Path

logger = logging.getLogger('telegram_bot.config')


class TelegramConfig:
    """Управление конфигурацией Telegram бота"""
    
    def __init__(self, config_path: Optional[str] = None):
        self.project_root = self._get_project_root()
        self.config_path = config_path or self.project_root / 'config' / 'telegram_config.yaml'
        print(f"Config path - {self.config_path}")
        self.config = self._load_config()
   
    def _get_project_root(self) -> Path:
        """Определяет корневую папку проекта по маркерным файлам"""
        current_path = Path(__file__).absolute()
        
        # Поднимаемся вверх по директориям, пока не найдем корень проекта
        for parent in current_path.parents:
            # Проверяем наличие маркерных файлов проекта
            if (parent / "setup_environment.py").exists():
                return parent
        
        # Если маркеры не найдены, используем логическое предположение о структуре
        # Из ml/data/providers/data_manager.py поднимаемся на 3 уровня вверх
        fallback_root = current_path.parent.parent.parent
        self.logger.warning(f"Маркеры проекта не найдены, используем fallback путь: {fallback_root}")
        return fallback_root
    
    def _load_config(self) -> Dict[str, Any]:
        """Загрузка конфигурации из YAML файла"""
        try:
            if not self.config_path.exists():
                logger.warning(f"⚠️ Файл конфигурации не найден: {self.config_path}")
                return self._create_default_config()
            
            with open(self.config_path, 'r', encoding='utf-8') as f:
                config = yaml.safe_load(f)
            
            logger.info(f"✅ Конфигурация Telegram бота загружена из {self.config_path}")
            return config
            
        except Exception as e:
            logger.error(f"❌ Ошибка загрузки конфигурации: {e}")
            return self._create_default_config()
    
    def _create_default_config(self) -> Dict[str, Any]:
        """Создание конфигурации по умолчанию"""
        default_config = {
            'telegram': {
                'bot_token': '',
                'chat_id': '',
                'notifications': {
                    'training_complete': True,
                    'predictions_generated': True,
                    'errors': True,
                    'warnings': True
                },
                'polling': {
                    'timeout': 30,
                    'interval': 1
                },
                'security': {
                    'allowed_users': [],
                    'require_auth': True
                },
                'logging': {
                    'level': 'INFO',
                    'file': 'data/logs/telegram_bot.log'  # 🔧 ИСПРАВЛЕНО
                }
            },
            'ml_integration': {
                'config_path': 'config/orchestrator_config.yaml',
                'model_path': 'data/models/enhanced_predictor_v2.pth',
                'dataset_path': 'data/datasets/dataset.json'
            }
        }
        
        try:
            # 🔧 СОЗДАЕМ ДИРЕКТОРИЮ ДЛЯ ЛОГОВ ЗАРАНЕЕ
            log_path = self.project_root / 'data' / 'logs'
            log_path.mkdir(parents=True, exist_ok=True)
            
            with open(self.config_path, 'w', encoding='utf-8') as f:
                yaml.dump(default_config, f, default_flow_style=False, allow_unicode=True)
            
            logger.info(f"✅ Создана конфигурация по умолчанию: {self.config_path}")
            
        except Exception as e:
            logger.error(f"❌ Ошибка создания конфигурации по умолчанию: {e}")
        
        return default_config
    
    def get_logging_config(self) -> Dict[str, Any]:
        """Получение конфигурации логирования"""
        return self.config.get('telegram', {}).get('logging', {})
    
    def get_log_file_path(self) -> Path:
        """Получение полного пути к файлу логов"""
        log_file = self.get_logging_config().get('file', 'data/logs/telegram_bot.log')
        return self.project_root / log_file
    
    def get_log_level(self) -> str:
        """Получение уровня логирования"""
        return self.get_logging_config().get('level', 'INFO')
    
    def get_bot_token(self) -> str:
        """Получение bot token"""
        return self.config.get('telegram', {}).get('bot_token', '')
    
    def get_chat_id(self) -> str:
        """Получение chat_id"""
        return self.config.get('telegram', {}).get('chat_id', '')
    
    def is_enabled(self) -> bool:
        """Проверка включен ли бот (имеет ли токен и chat_id)"""
        return bool(self.get_bot_token()) and bool(self.get_chat_id())
    
    def get_notification_settings(self) -> Dict[str, bool]:
        """Получение настроек уведомлений"""
        return self.config.get('telegram', {}).get('notifications', {})
    
    def validate_config(self) -> bool:
        """Валидация конфигурации"""
        if not self.get_bot_token():
            logger.error("❌ Bot token не указан в конфигурации")
            return False
        
        if not self.get_chat_id():
            logger.error("❌ Chat ID не указан в конфигурации")
            return False
        
        logger.info("✅ Конфигурация Telegram бота валидна")
        return True
    
    def get_polling_settings(self) -> Dict[str, Any]:
        """Получение настроек опроса"""
        return self.config.get('telegram', {}).get('polling', {})
    
    def get_security_settings(self) -> Dict[str, Any]:
        """Получение настроек безопасности"""
        return self.config.get('telegram', {}).get('security', {})
    
    def get_ml_integration_settings(self) -> Dict[str, Any]:
        """Получение настроек интеграции с ML"""
        return self.config.get('ml_integration', {})
