# services/telegram/security.py
"""
Модуль безопасности Telegram бота
"""

import logging
from typing import Dict  # ← ДОБАВЛЯЕМ ИМПОРТ
from config.paths import TELEGRAM_CONFIG_FILE
import json

logger = logging.getLogger('telegram_bot')

class SecurityManager:
    """Менеджер безопасности бота"""
    
    def __init__(self):
        self.config = self._load_config()
    
    def _load_config(self) -> Dict:  # ← ТЕПЕРЬ Dict ОПРЕДЕЛЕН
        """Загрузка конфигурации"""
        try:
            with open(TELEGRAM_CONFIG_FILE, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception as e:
            logger.error(f"❌ Ошибка загрузки конфига безопасности: {e}")
            return {}
    
    def is_authorized_user(self, chat_id: int) -> bool:
        """Проверка авторизации пользователя"""
        allowed_chat_id = self.config.get('chat_id')
        is_authorized = str(chat_id) == str(allowed_chat_id)
        
        if not is_authorized:
            logger.warning(f"🚫 Неавторизованный доступ от chat_id: {chat_id}")
        
        return is_authorized
    
    def validate_message(self, message: Dict) -> bool:
        """Валидация входящего сообщения"""
        required_fields = ['message_id', 'chat', 'text']
        
        for field in required_fields:
            if field not in message:
                logger.error(f"❌ Отсутствует обязательное поле: {field}")
                return False
        
        if 'text' not in message or not message['text'].strip():
            logger.error("❌ Пустое текстовое сообщение")
            return False
        
        return True
    
    def sanitize_input(self, text: str) -> str:
        """Санитизация ввода"""
        # Удаляем потенциально опасные символы
        dangerous_chars = ['<', '>', '&', '"', "'", '`', '|', ';', '$', '(', ')', '`']
        sanitized = text
        for char in dangerous_chars:
            sanitized = sanitized.replace(char, '')
        
        # Ограничиваем длину
        max_length = 100
        if len(sanitized) > max_length:
            sanitized = sanitized[:max_length]
            logger.warning(f"📏 Сообщение обрезано до {max_length} символов")
        
        return sanitized.strip()
