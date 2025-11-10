# [file name]: services/telegram/bot.py
"""
Telegram Polling Bot - ПОЛНОСТЬЮ ОБНОВЛЕННЫЙ
"""
import sys
sys.path.insert(0, '/opt/dev')
import os
import time

from config.logging_config import get_telegram_bot_logger
from services.telegram.config import TelegramConfig
from services.telegram.security import SecurityManager
from services.telegram.commands import CommandHandler
from services.telegram.handlers import MessageHandler
from services.telegram.utils import SystemChecker, MessageSender

# ⚡ КОРРЕКТНАЯ ИНИЦИАЛИЗАЦИЯ АВТОСЕРВИСА
try:
    from services.auto_learning.service import AutoLearningService
    AUTO_SERVICE_AVAILABLE = True
except ImportError as e:
    print(f"⚠️ AutoLearningService не доступен: {e}")
    AutoLearningService = None
    AUTO_SERVICE_AVAILABLE = False

logger = get_telegram_bot_logger()

class TelegramPollingBot:
    """Telegram бот для управления системой через Long Polling"""
    
    def __init__(self):
        # Инициализация компонентов
        self.config_manager = TelegramConfig()
        self.config = self.config_manager.config
        self.last_update_id = 0
        
        # Инициализация сервисов
        self.auto_service = None
        self.init_auto_service()
        
        # Инициализация модулей бота
        self.security_manager = SecurityManager()
        self.command_handler = CommandHandler(self.auto_service)
        self.message_handler = MessageHandler(self.command_handler, self.security_manager)
        
        # 🔧 ИСПРАВЛЕНИЕ: Правильная инициализация MessageSender
        bot_token = self.config_manager.get_bot_token()
        if bot_token:
            self.message_sender = MessageSender(bot_token)
            logger.info("✅ MessageSender инициализирован")
        else:
            logger.error("❌ Bot token не найден, MessageSender не инициализирован")
            self.message_sender = None
    
    def init_auto_service(self):
        """Инициализация автосервиса для интеграции"""
        if not AUTO_SERVICE_AVAILABLE:
            logger.warning("⚠️ AutoLearningService недоступен для Telegram бота")
            return
            
        try:
            self.auto_service = AutoLearningService()
            logger.info("✅ Автосервис инициализирован для Telegram бота")
        except Exception as e:
            logger.error(f"❌ Ошибка инициализации автосервиса: {e}")
            self.auto_service = None
    
    def get_updates(self):
        """Получение обновлений от Telegram API"""
        if not self.config_manager.is_enabled():
            logger.debug("❌ Telegram бот отключен в конфигурации")
            return []
        
        bot_token = self.config_manager.get_bot_token()
        if not bot_token:
            logger.error("❌ Bot token не найден в конфиге")
            return []
        
        try:
            import requests
            url = f"https://api.telegram.org/bot{bot_token}/getUpdates"
            params = {
                'offset': self.last_update_id + 1,
                'timeout': 30,
                'allowed_updates': ['message']
            }
            
            response = requests.get(url, params=params, timeout=35)
            if response.status_code == 200:
                data = response.json()
                if data.get('ok'):
                    updates = data.get('result', [])
                    if updates:
                        self.last_update_id = updates[-1]['update_id']
                    return updates
            else:
                logger.error(f"❌ Ошибка API Telegram: {response.status_code}")
                if response.status_code == 409:
                    logger.warning("⚠️ Конфликт offset, сбрасываем...")
                    self.last_update_id = 0
            return []
            
        except Exception as e:
            logger.error(f"❌ Ошибка получения updates: {e}")
            return []
    
    def process_message(self, message):
        """Обработка входящих сообщений через модуль обработки"""
        try:
            # Валидация сообщения
            if not self.security_manager.validate_message(message):
                logger.error("❌ Невалидное сообщение")
                return
            
            text = message.get('text', '').strip()
            chat_id = message['chat']['id']
            
            logger.info(f"📨 Обработка команды: {text} от {chat_id}")
            
            # Обработка через модуль обработки сообщений
            response = self.message_handler.process_message(message)
            
            # Отправка ответа
            if response and self.message_sender:
                self.send_message(chat_id, response)
            
        except Exception as e:
            logger.error(f"❌ Ошибка обработки сообщения: {e}")
            # Пытаемся отправить сообщение об ошибке
            try:
                chat_id = message.get('chat', {}).get('id')
                if chat_id and self.message_sender:
                    self.send_message(chat_id, f"❌ Ошибка обработки команды: {e}")
            except:
                pass
    
    def send_message(self, chat_id, text, parse_mode='HTML'):
        """Отправка сообщения через модуль отправки"""
        if not self.message_sender:
            logger.error("❌ MessageSender не инициализирован")
            return False
        return self.message_sender.send_message(chat_id, text, parse_mode)
    
    def start_polling(self):
        """Запуск polling бота"""
        if not self.config_manager.is_enabled():
            logger.error("❌ Telegram бот отключен в конфигурации")
            return
        
        if not self.config_manager.validate_config():
            logger.error("❌ Невалидная конфигурация Telegram бота")
            return
        
        logger.info("🔍 Запуск Telegram polling бота...")
        logger.info(f"🤖 Бот token: {self.config_manager.get_bot_token()[:10]}...")
        logger.info(f"💬 Разрешенный chat_id: {self.config_manager.get_chat_id()}")
        
        try:
            # Тестовое сообщение при запуске
            chat_id = self.config_manager.get_chat_id()
            if chat_id and self.message_sender:
                self.send_message(
                    chat_id, 
                    "🤖 <b>Telegram бот запущен!</b>\n\n"
                    "Система мониторинга и управления AI Prediction System активирована.\n"
                    "Используйте /help для списка команд."
                )
        except Exception as e:
            logger.warning(f"⚠️ Не удалось отправить стартовое сообщение: {e}")
        
        # Основной цикл polling
        error_count = 0
        max_errors = 5
        
        while True:
            try:
                updates = self.get_updates()
                for update in updates:
                    if 'message' in update:
                        self.process_message(update['message'])
                
                # Сбрасываем счетчик ошибок при успешной итерации
                error_count = 0
                time.sleep(1)
                
            except KeyboardInterrupt:
                logger.info("🛑 Бот остановлен пользователем")
                self.send_shutdown_message()
                break
            except Exception as e:
                error_count += 1
                logger.error(f"❌ Ошибка в основном цикле (#{error_count}): {e}")
                
                if error_count >= max_errors:
                    logger.error(f"🚨 Достигнут максимум ошибок ({max_errors}). Останавливаем бота.")
                    self.send_error_message(f"Критическая ошибка бота: {e}")
                    break
                
                time.sleep(10)
    
    def send_shutdown_message(self):
        """Отправка сообщения о shutdown"""
        try:
            chat_id = self.config_manager.get_chat_id()
            if chat_id and self.message_sender:
                self.message_sender.send_message(
                    chat_id,
                    "🛑 <b>Telegram бот остановлен</b>\n\n"
                    "Система мониторинга приостановлена.\n"
                    "Для возобновления работы перезапустите бота."
                )
        except Exception as e:
            logger.error(f"❌ Ошибка отправки shutdown сообщения: {e}")
    
    def send_error_message(self, error_text):
        """Отправка сообщения об ошибке"""
        try:
            chat_id = self.config_manager.get_chat_id()
            if chat_id and self.message_sender:
                self.message_sender.send_message(
                    chat_id,
                    f"🚨 <b>КРИТИЧЕСКАЯ ОШИБКА</b>\n\n"
                    f"Telegram бот остановлен из-за ошибок:\n"
                    f"<code>{error_text}</code>\n\n"
                    f"Требуется перезапуск бота."
                )
        except Exception as e:
            logger.error(f"❌ Ошибка отправки error сообщения: {e}")
    
    def get_bot_info(self):
        """Получение информации о боте"""
        return {
            'enabled': self.config_manager.is_enabled(),
            'bot_token_set': bool(self.config_manager.get_bot_token()),
            'chat_id_set': bool(self.config_manager.get_chat_id()),
            'auto_service_available': self.auto_service is not None,
            'message_sender_available': self.message_sender is not None,
            'last_update_id': self.last_update_id,
            'config_valid': self.config_manager.validate_config()
        }


def main():
    """Основная функция запуска бота"""
    try:
        logger.info("🚀 Запуск Telegram бота...")
        
        bot = TelegramPollingBot()
        
        # Проверка конфигурации
        bot_info = bot.get_bot_info()
        logger.info(f"📋 Информация о боте: {bot_info}")
        
        if not bot_info['enabled']:
            logger.warning("⚠️ Бот отключен в конфигурации. Запуск отменен.")
            return
        
        if not bot_info['config_valid']:
            logger.error("❌ Невалидная конфигурация бота. Запуск отменен.")
            return
        
        # Запуск polling
        bot.start_polling()
        
    except KeyboardInterrupt:
        logger.info("🛑 Бот остановлен по запросу пользователя")
    except Exception as e:
        logger.error(f"❌ Критическая ошибка запуска бота: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
