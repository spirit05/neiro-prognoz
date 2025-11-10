# services/telegram/handlers.py
"""
Обработчики сообщений Telegram бота
"""

import logging
from typing import Dict, Callable
from .commands import CommandHandler
from .security import SecurityManager

logger = logging.getLogger('telegram_bot')

class MessageHandler:
    """Обработчик входящих сообщений"""
    
    def __init__(self, command_handler: CommandHandler, security_manager: SecurityManager):
        self.command_handler = command_handler
        self.security_manager = security_manager
    
    def process_message(self, message: Dict) -> str:
        """Обработка входящего сообщения"""
        try:
            text = message.get('text', '').strip()
            chat_id = message['chat']['id']
            
            logger.info(f"📨 Обработка команды: {text} от {chat_id}")
            
            # Проверка авторизации
            if not self.security_manager.is_authorized_user(chat_id):
                return "❌ Доступ запрещен"
            
            # Обработка команды
            return self.command_handler.handle_command(text, chat_id)
            
        except Exception as e:
            logger.error(f"❌ Ошибка обработки сообщения: {e}")
            return f"❌ Ошибка обработки сообщения: {e}"
    
    def handle_unknown_command(self, chat_id: int) -> str:
        """Обработка неизвестной команды"""
        return "❌ Неизвестная команда. Используйте /help"
