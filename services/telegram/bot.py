"""
Основной файл Telegram бота для новой ML системы
Использует только WorkflowManager через MLDispatcher
"""

import os
import sys
import time
import logging
import signal
from typing import Dict, Any, Optional
from pathlib import Path

# Настройка пути для импортов
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

# Локальные импорты
from .config import TelegramConfig
from .logging_config import setup_telegram_logging, get_telegram_logger
from .security import SecurityManager
from .ml_dispatcher import MLDispatcher
from .handlers import MessageHandler
from .commands import CommandHandler

# Настройка логирования ДО создания экземпляров классов
config = TelegramConfig()
logger = setup_telegram_logging(config)

class TelegramBot:
    """Основной класс Telegram бота для новой ML системы"""
    
    def __init__(self):
        # Инициализация компонентов
        self.config = config
        self.running = False
        self.last_update_id = 0
        
        # Инициализация менеджеров
        self.security_manager = SecurityManager(self.config)
        self.ml_dispatcher = MLDispatcher()
        self.command_handler = CommandHandler(self.ml_dispatcher, self.security_manager)
        self.message_handler = MessageHandler(self.security_manager, self.command_handler)
        
        # Настройка обработчика сигналов для graceful shutdown
        signal.signal(signal.SIGINT, self._signal_handler)
        signal.signal(signal.SIGTERM, self._signal_handler)
        
        logger.info("✅ TelegramBot инициализирован")
    
    def _signal_handler(self, signum, frame):
        """Обработчик сигналов для graceful shutdown"""
        logger.info(f"📶 Получен сигнал {signum}, завершаем работу...")
        self.running = False
    
    def initialize_ml_system(self) -> bool:
        """Инициализация ML системы"""
        try:
            logger.info("🔄 Инициализация ML системы...")
            success = self.ml_dispatcher.initialize()
            
            if success:
                logger.info("✅ ML система успешно инициализирована")
                return True
            else:
                logger.error("❌ Не удалось инициализировать ML систему")
                return False
                
        except Exception as e:
            logger.error(f"❌ Ошибка инициализации ML системы: {e}")
            return False
    
    def validate_configuration(self) -> bool:
        """Валидация конфигурации бота"""
        try:
            # Проверка конфигурации Telegram
            if not self.config.validate_config():
                logger.error("❌ Конфигурация Telegram бота невалидна")
                return False
            
            # Проверка ML системы
            if not self.ml_dispatcher.is_initialized:
                logger.warning("⚠️ ML система не инициализирована, попытка инициализации...")
                if not self.initialize_ml_system():
                    logger.error("❌ Не удалось инициализировать ML систему")
                    return False
            
            logger.info("✅ Конфигурация бота валидна")
            return True
            
        except Exception as e:
            logger.error(f"❌ Ошибка валидации конфигурации: {e}")
            return False
    
    def get_updates(self) -> list:
        """Получение обновлений от Telegram API"""
        import requests
        
        bot_token = self.config.get_bot_token()
        if not bot_token:
            logger.error("❌ Bot token не установлен")
            return []
        
        try:
            url = f"https://api.telegram.org/bot{bot_token}/getUpdates"
            params = {
                'offset': self.last_update_id + 1,
                'timeout': self.config.get_polling_settings().get('timeout', 30),
                'allowed_updates': ['message']
            }
            
            response = requests.get(url, params=params, timeout=35)
            
            if response.status_code == 200:
                data = response.json()
                if data.get('ok'):
                    updates = data.get('result', [])
                    if updates:
                        self.last_update_id = updates[-1]['update_id']
                        logger.debug(f"📥 Получено {len(updates)} обновлений, последний ID: {self.last_update_id}")
                    return updates
                else:
                    logger.error(f"❌ Telegram API вернул ошибку: {data}")
            else:
                logger.error(f"❌ Ошибка HTTP при получении обновлений: {response.status_code}")
                
                # Обработка конфликта offset
                if response.status_code == 409:
                    logger.warning("⚠️ Конфликт offset, сбрасываем...")
                    self.last_update_id = 0
            
            return []
            
        except requests.exceptions.Timeout:
            logger.debug("⏱ Таймаут при получении обновлений")
            return []
        except Exception as e:
            logger.error(f"❌ Ошибка получения обновлений: {e}")
            return []
    
    def send_message(self, chat_id: int, text: str, parse_mode: str = 'HTML') -> bool:
        """Отправка сообщения в Telegram"""
        import requests
        
        bot_token = self.config.get_bot_token()
        if not bot_token:
            logger.error("❌ Bot token не установлен, невозможно отправить сообщение")
            return False
        
        try:
            url = f"https://api.telegram.org/bot{bot_token}/sendMessage"
            
            payload = {
                'chat_id': chat_id,
                'text': text,
                'parse_mode': parse_mode,
                'disable_web_page_preview': True
            }
            
            response = requests.post(url, json=payload, timeout=10)
            
            if response.status_code == 200:
                logger.debug(f"✅ Сообщение отправлено в чат {chat_id}")
                return True
            else:
                logger.error(f"❌ Ошибка отправки сообщения: {response.status_code} - {response.text}")
                return False
                
        except Exception as e:
            logger.error(f"❌ Ошибка отправки сообщения: {e}")
            return False
    
    def process_updates(self, updates: list):
        """Обработка полученных обновлений"""
        for update in updates:
            if 'message' in update:
                self.process_message(update['message'])
    
    def process_message(self, message: Dict[str, Any]):
        """Обработка одного сообщения"""
        try:
            # Обрабатываем сообщение через handler
            response = self.message_handler.process_message(message)
            
            # Отправляем ответ если есть
            if response:
                chat_id = message['chat']['id']
                self.send_message(chat_id, response)
                
        except Exception as e:
            logger.error(f"❌ Ошибка обработки сообщения: {e}")
    
    def send_startup_message(self):
        """Отправка сообщения о запуске бота"""
        try:
            chat_id = self.config.get_chat_id()
            if not chat_id:
                logger.warning("⚠️ Chat ID не установлен, пропускаем startup сообщение")
                return
            
            # Получаем статус системы
            status = self.ml_dispatcher.get_system_status()
            
            message = "🚀 <b>TELEGRAM БОТ ЗАПУЩЕН</b>\n\n"
            message += "Новый бот для AI Prediction System активирован!\n\n"
            
            # Информация о системе
            message += "📊 <b>Статус системы:</b>\n"
            message += f"• ML система: {'✅ Инициализирована' if status.get('is_initialized') else '❌ Ошибка'}\n"
            message += f"• Модель: {'✅ Обучена' if status.get('is_trained') else '❌ Не обучена'}\n"
            message += f"• Данные: {status.get('dataset_size', 0)} групп\n\n"
            
            # Команды
            message += "📋 <b>Основные команды:</b>\n"
            message += "/start - Начало работы\n"
            message += "/help - Справка по командам\n"
            message += "/status - Статус системы\n"
            message += "/train - Обучение модели\n\n"
            
            message += "🔧 <b>Архитектура:</b> Новая модульная (Этап 11)\n"
            message += "🤖 <b>Интеграция:</b> WorkflowManager"
            
            self.send_message(chat_id, message)
            logger.info("✅ Startup сообщение отправлено")
            
        except Exception as e:
            logger.error(f"❌ Ошибка отправки startup сообщения: {e}")
    
    def run(self):
        """Основной цикл работы бота"""
        # Проверка конфигурации
        if not self.validate_configuration():
            logger.error("❌ Конфигурация невалидна, бот не может быть запущен")
            return
        
        # Отправка сообщения о запуске
        self.send_startup_message()
        
        # Основной цикл опроса
        self.running = True
        error_count = 0
        max_errors = 10
        
        logger.info("🔄 Запуск основного цикла опроса...")
        
        while self.running:
            try:
                # Получение обновлений
                updates = self.get_updates()
                
                # Обработка обновлений
                if updates:
                    self.process_updates(updates)
                    error_count = 0  # Сбрасываем счетчик ошибок при успешной итерации
                else:
                    # Если обновлений нет, небольшая пауза
                    time.sleep(self.config.get_polling_settings().get('interval', 1))
                
            except KeyboardInterrupt:
                logger.info("🛑 Бот остановлен пользователем (Ctrl+C)")
                self.running = False
                break
                
            except Exception as e:
                error_count += 1
                logger.error(f"❌ Ошибка в основном цикле (#{error_count}): {e}")
                
                if error_count >= max_errors:
                    logger.error(f"🚨 Достигнут максимум ошибок ({max_errors}), останавливаем бота")
                    self.send_error_notification(f"Критическая ошибка бота после {max_errors} попыток: {e}")
                    self.running = False
                    break
                
                # Пауза перед повторной попыткой
                time.sleep(10)
        
        # Завершение работы
        logger.info("🛑 Telegram бот остановлен")
        self.send_shutdown_message()
    
    def send_shutdown_message(self):
        """Отправка сообщения об остановке бота"""
        try:
            chat_id = self.config.get_chat_id()
            if not chat_id:
                return
            
            message = "🛑 <b>TELEGRAM БОТ ОСТАНОВЛЕН</b>\n\n"
            message += "Система мониторинга приостановлена.\n"
            message += "Для возобновления работы перезапустите бота."
            
            self.send_message(chat_id, message)
            logger.info("✅ Shutdown сообщение отправлено")
            
        except Exception as e:
            logger.error(f"❌ Ошибка отправки shutdown сообщения: {e}")
    
    def send_error_notification(self, error_text: str):
        """Отправка уведомления об ошибке"""
        try:
            chat_id = self.config.get_chat_id()
            if not chat_id:
                return
            
            message = f"🚨 <b>КРИТИЧЕСКАЯ ОШИБКА</b>\n\n"
            message += f"Telegram бот остановлен из-за ошибок:\n"
            message += f"<code>{error_text[:200]}</code>\n\n"
            message += f"Требуется перезапуск бота."
            
            self.send_message(chat_id, message)
            
        except Exception as e:
            logger.error(f"❌ Ошибка отправки error сообщения: {e}")


def main():
    """Основная функция запуска бота"""
    logger.info("🚀 Запуск Telegram бота для новой ML системы...")
    
    try:
        # Создаем и запускаем бота
        bot = TelegramBot()
        bot.run()
        
    except KeyboardInterrupt:
        logger.info("🛑 Бот остановлен по запросу пользователя")
    except Exception as e:
        logger.error(f"❌ Критическая ошибка запуска бота: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()#/opt/model/services/telegram/bot.py
