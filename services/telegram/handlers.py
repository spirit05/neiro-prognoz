#/opt/model/services/telegram/handlers.py
"""
Обработчики сообщений для Telegram бота
"""

import logging
from typing import Dict, Any, Callable, Optional
from .security import SecurityManager
from .commands import CommandHandler

logger = logging.getLogger('telegram_bot.handlers')


class MessageHandler:
    """Обработчик входящих сообщений Telegram"""
    
    def __init__(self, security_manager: SecurityManager, command_handler: CommandHandler):
        self.security_manager = security_manager
        self.command_handler = command_handler
    
    def process_message(self, message: Dict[str, Any]) -> Optional[str]:
        """Обработка входящего сообщения"""
        try:
            # Валидация сообщения
            if not self.security_manager.validate_message(message):
                return "❌ Невалидное сообщение"
            
            chat_id = message['chat']['id']
            text = message.get('text', '').strip()
            
            logger.info(f"📨 Обработка сообщения от {chat_id}: {text[:50]}...")
            
            # Проверка авторизации
            if not self.security_manager.is_authorized_user(chat_id):
                return "❌ Доступ запрещен. Ваш user_id не авторизован."
            
            # Обработка команды
            response = self.command_handler.handle_command(text, chat_id)
            
            return response
            
        except Exception as e:
            logger.error(f"❌ Ошибка обработки сообщения: {e}")
            return f"❌ Ошибка обработки команды: {str(e)[:100]}"
    
    def handle_unknown_command(self, chat_id: int) -> str:
        """Обработка неизвестной команды"""
        return (
            "❌ Неизвестная команда.\n\n"
            "📋 Доступные команды:\n"
            "/start - Начало работы\n"
            "/help - Справка по командам\n"
            "/status - Статус системы\n"
            "/predictions - Последние прогнозы\n"
            "/data - Информация о данных\n"
            "/train - Обучение модели\n"
            "/results - Аналитика обучения\n"
            "/add - Добавить группу вручную\n"
            "/version - Версия системы"
        )
