# telegram_polling.py - АЛЬТЕРНАТИВА WEBHOOK
#!/usr/bin/env python3
"""
Telegram бот через Long Polling (без вебхука)
"""

import os
import sys
import time
import logging
import requests
from datetime import datetime

PROJECT_PATH = '/opt/project'
sys.path.insert(0, PROJECT_PATH)
sys.path.insert(0, os.path.dirname(__file__))

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger('TelegramPolling')

class TelegramPollingBot:
    def __init__(self):
        self.config = self.load_config()
        self.last_update_id = 0
        self.auto_service = None
        self.init_auto_service()
    
    def load_config(self):
        """Загрузка конфигурации"""
        config_path = os.path.join(os.path.dirname(__file__), 'telegram_config.json')
        try:
            with open(config_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        except:
            return {'enabled': False}
    
    def init_auto_service(self):
        """Инициализация автосервиса"""
        try:
            from auto_learning_service import AutoLearningService
            self.auto_service = AutoLearningService()
            logger.info("✅ Автосервис инициализирован для polling бота")
        except Exception as e:
            logger.error(f"❌ Ошибка инициализации автосервиса: {e}")
    
    def get_updates(self):
        """Получение обновлений от Telegram"""
        if not self.config.get('enabled', False):
            return []
        
        bot_token = self.config.get('bot_token')
        if not bot_token:
            return []
        
        try:
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
            return []
            
        except Exception as e:
            logger.error(f"❌ Ошибка получения updates: {e}")
            return []
    
    def process_message(self, message):
        """Обработка сообщения"""
        text = message.get('text', '').strip()
        chat_id = message['chat']['id']
        
        logger.info(f"📨 Обработка команды: {text} от {chat_id}")
        
        if text == '/start':
            response = "🤖 <b>AI Prediction System активирован!</b>\n\n" \
                      "Доступные команды:\n" \
                      "/status - статус системы\n" \
                      "/predictions - последние прогнозы\n" \
                      "/help - помощь"
            self.send_message(chat_id, response)
            
        elif text == '/status':
            self.send_system_status(chat_id)
            
        elif text == '/predictions':
            self.send_last_predictions(chat_id)
            
        elif text == '/help':
            response = "🆘 <b>Помощь по командам:</b>\n\n" \
                      "/status - полный статус системы\n" \
                      "/predictions - последние 4 прогноза\n" \
                      "/help - эта справка"
            self.send_message(chat_id, response)
            
        else:
            self.send_message(chat_id, "❌ Неизвестная команда. Используйте /help")
    
    def send_message(self, chat_id, text):
        """Отправка сообщения"""
        try:
            bot_token = self.config.get('bot_token')
            url = f"https://api.telegram.org/bot{bot_token}/sendMessage"
            
            payload = {
                'chat_id': chat_id,
                'text': text,
                'parse_mode': 'HTML'
            }
            
            response = requests.post(url, json=payload, timeout=10)
            if response.status_code == 200:
                logger.info(f"✅ Сообщение отправлено в чат {chat_id}")
                return True
            else:
                logger.error(f"❌ Ошибка отправки: {response.text}")
                return False
                
        except Exception as e:
            logger.error(f"❌ Ошибка отправки сообщения: {e}")
            return False
    
    def send_system_status(self, chat_id):
        """Отправка статуса системы"""
        try:
            if self.auto_service:
                status_data = self.auto_service.get_service_status()
                
                message = "🤖 <b>СТАТУС СИСТЕМЫ</b>\n\n"
                message += f"✅ Модель: {'Обучена' if status_data.get('model_trained') else 'Не обучена'}\n"
                message += f"📊 Групп в датасете: {status_data.get('dataset_size', 0)}\n"
                message += f"🌐 Веб-версия: {'Запущена' if status_data.get('web_running') else 'Не запущена'}\n"
                message += f"🔧 Автосервис: {'Активен' if status_data.get('service_active') else 'Остановлен'}\n"
                message += f"🕐 Последний тираж: {status_data.get('last_processed_draw', 'Нет')}\n"
                
                # Добавляем прогнозы если есть
                predictions = status_data.get('last_predictions', [])
                if predictions:
                    message += "\n🔮 <b>ПОСЛЕДНИЕ ПРОГНОЗЫ:</b>\n"
                    for i, (group, score) in enumerate(predictions[:4], 1):
                        confidence = "🟢" if score > 0.02 else "🟡" if score > 0.01 else "🔴"
                        message += f"{i}. {group[0]} {group[1]} {group[2]} {group[3]} {confidence}\n"
                
                self.send_message(chat_id, message)
            else:
                self.send_message(chat_id, "❌ Сервис временно недоступен")
                
        except Exception as e:
            logger.error(f"❌ Ошибка отправки статуса: {e}")
            self.send_message(chat_id, f"❌ Ошибка получения статуса: {e}")
    
    def send_last_predictions(self, chat_id):
        """Отправка последних прогнозов"""
        try:
            from model.data_loader import load_predictions
            predictions = load_predictions()
            
            if predictions:
                message = "🔮 <b>ПОСЛЕДНИЕ ПРОГНОЗЫ</b>\n\n"
                for i, (group, score) in enumerate(predictions[:4], 1):
                    confidence = "🟢" if score > 0.02 else "🟡" if score > 0.01 else "🔴"
                    message += f"{i}. {group[0]} {group[1]} {group[2]} {group[3]}\n"
                    message += f"   Уверенность: {score:.4f} {confidence}\n\n"
            else:
                message = "📝 Прогнозы еще не сгенерированы"
                
            self.send_message(chat_id, message)
            
        except Exception as e:
            logger.error(f"❌ Ошибка отправки прогнозов: {e}")
            self.send_message(chat_id, f"❌ Ошибка получения прогнозов: {e}")
    
    def start_polling(self):
        """Запуск polling бота"""
        if not self.config.get('enabled', False):
            logger.error("❌ Telegram не настроен в конфиге")
            return
        
        logger.info("🔍 Запуск Telegram polling бота...")
        
        while True:
            try:
                updates = self.get_updates()
                for update in updates:
                    if 'message' in update:
                        self.process_message(update['message'])
                
                time.sleep(1)
                
            except KeyboardInterrupt:
                logger.info("🛑 Бот остановлен пользователем")
                break
            except Exception as e:
                logger.error(f"❌ Ошибка в основном цикле: {e}")
                time.sleep(10)

if __name__ == "__main__":
    bot = TelegramPollingBot()
    bot.start_polling()