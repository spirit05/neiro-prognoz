#/opt/model/services/telegram/security.py
"""
Безопасность Telegram бота - проверка доступа и валидация
"""

import logging
from typing import Dict, Any, Optional, List
from .config import TelegramConfig

logger = logging.getLogger('telegram_bot.security')


class SecurityManager:
    """Менеджер безопасности для Telegram бота"""
    
    def __init__(self, config: TelegramConfig):
        self.config = config
        self.security_settings = config.get_security_settings()
    
    def is_authorized_user(self, user_id: int) -> bool:
        """Проверка авторизации пользователя"""
        try:
            # Основной chat_id из конфигурации
            allowed_chat_id = self.config.get_chat_id()
            
            # Проверяем основной chat_id
            if str(user_id) == str(allowed_chat_id):
                return True
            
            # Проверяем дополнительные пользователи
            allowed_users = self.security_settings.get('allowed_users', [])
            if str(user_id) in [str(u) for u in allowed_users]:
                return True
            
            # Если require_auth выключен, разрешаем всем (не рекомендуется)
            if not self.security_settings.get('require_auth', True):
                logger.warning(f"⚠️ Доступ разрешен без авторизации для {user_id}")
                return True
            
            logger.warning(f"🚫 Неавторизованный доступ от user_id: {user_id}")
            return False
            
        except Exception as e:
            logger.error(f"❌ Ошибка проверки авторизации: {e}")
            return False
    
    def validate_message(self, message: Dict[str, Any]) -> bool:
        """Валидация входящего сообщения"""
        required_fields = ['message_id', 'chat', 'text']
        
        for field in required_fields:
            if field not in message:
                logger.error(f"❌ Отсутствует обязательное поле: {field}")
                return False
        
        chat = message.get('chat', {})
        if 'id' not in chat:
            logger.error("❌ В сообщении отсутствует chat.id")
            return False
        
        text = message.get('text', '').strip()
        if not text:
            logger.error("❌ Пустое текстовое сообщение")
            return False
        
        # Проверка максимальной длины
        if len(text) > 500:
            logger.warning(f"📏 Сообщение слишком длинное ({len(text)} символов)")
        
        return True
    
    def sanitize_input(self, text: str, max_length: int = 500) -> str:
        """Санитизация ввода"""
        # Удаляем опасные символы
        dangerous_chars = ['<', '>', '&', '"', "'", '`', '|', ';', '$', '(', ')', '`', '\\']
        sanitized = text
        
        for char in dangerous_chars:
            sanitized = sanitized.replace(char, '')
        
        # Ограничиваем длину
        if len(sanitized) > max_length:
            sanitized = sanitized[:max_length]
            logger.warning(f"📏 Ввод обрезан до {max_length} символов")
        
        return sanitized.strip()
    
    def validate_group_input(self, text: str) -> Optional[List[int]]:
        """Валидация ввода группы чисел (например, "1 2 3 4")"""
        try:
            # Удаляем лишние пробелы и разделяем
            parts = text.strip().split()
            
            if len(parts) != 4:
                return None
            
            # Пытаемся преобразовать в числа
            numbers = []
            for part in parts:
                num = int(part)
                if num < 1 or num > 26:
                    return None
                numbers.append(num)
            
            return numbers
            
        except (ValueError, TypeError):
            return None
    
    def get_authorized_users(self) -> List[str]:
        """Получение списка авторизованных пользователей"""
        users = []
        
        main_chat_id = self.config.get_chat_id()
        if main_chat_id:
            users.append(str(main_chat_id))
        
        additional_users = self.security_settings.get('allowed_users', [])
        users.extend([str(u) for u in additional_users])
        
        return users
