#!/usr/bin/env python3
"""
Telegram бот через Long Polling (без вебхука)
"""

import os
import sys
import time
import json
import logging
import requests
from datetime import datetime

# Настройка путей
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
        except Exception as e:
            logger.error(f"❌ Ошибка загрузки конфига: {e}")
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
                    "/autoprognoz - включить/выключить авто-прогнозы\n" \
                    "/help - помощь"
            self.send_message(chat_id, response)
            
        elif text == '/status':
            self.send_system_status(chat_id)
            
        elif text == '/predictions':
            self.send_last_predictions(chat_id)
            
        elif text == '/autoprognoz':
            self.toggle_auto_predictions(chat_id)
            
        elif text == '/help':
            response = "🆘 <b>Помощь по командам:</b>\n\n" \
                    "/status - полный статус системы\n" \
                    "/predictions - последние 4 прогноза\n" \
                    "/autoprognoz - включить/выключить авто-прогнозы\n" \
                    "/help - эта справка"
            self.send_message(chat_id, response)
            
        else:
            self.send_message(chat_id, "❌ Неизвестная команда. Используйте /help")

    def toggle_auto_predictions(self, chat_id):
        """Включение/выключение авто-прогнозов"""
        try:
            # Загружаем текущий конфиг
            config_path = os.path.join(os.path.dirname(__file__), 'telegram_config.json')
            with open(config_path, 'r', encoding='utf-8') as f:
                config = json.load(f)
            
            # Переключаем настройку
            current_state = config.get('notifications', {}).get('predictions', False)
            new_state = not current_state
            
            # Обновляем конфиг
            if 'notifications' not in config:
                config['notifications'] = {}
            config['notifications']['predictions'] = new_state
            
            # Сохраняем
            with open(config_path, 'w', encoding='utf-8') as f:
                json.dump(config, f, ensure_ascii=False, indent=2)
            
            # Обновляем конфиг в боте
            self.config = config
            
            status = "ВКЛЮЧЕНЫ" if new_state else "ВЫКЛЮЧЕНЫ"
            message = f"🔔 Авто-прогнозы **{status}**\n\n"
            message += "Теперь после каждого дообучения новые прогнозы будут автоматически отправляться в этот чат." if new_state else "Автоматическая отправка прогнозов отключена."
            
            self.send_message(chat_id, message)
            logger.info(f"🔧 Авто-прогнозы {'включены' if new_state else 'выключены'} для чата {chat_id}")
            
        except Exception as e:
            logger.error(f"❌ Ошибка переключения авто-прогнозов: {e}")
            self.send_message(chat_id, f"❌ Ошибка: {e}")
      
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
        """Отправка статуса системы с аналитикой самообучения"""
        try:
            # 🔄 АКТУАЛЬНЫЕ ДАННЫЕ
            web_running = self.is_web_running()
            current_draw = self.get_current_draw()
            auto_service_running = self.is_auto_service_running()  # ← НОВАЯ ПРОВЕРКА
            
            if self.auto_service:
                status_data = self.auto_service.get_service_status()
                
                # 🔄 ПЕРЕЗАГРУЖАЕМ ДАННЫЕ САМООБУЧЕНИЯ
                try:
                    from model.self_learning import SelfLearningSystem
                    learning_system = SelfLearningSystem("/opt/project/data/learning_results.json")
                    learning_stats = learning_system.get_performance_stats()
                except Exception as e:
                    logger.error(f"❌ Ошибка загрузки аналитики: {e}")
                    learning_stats = status_data.get('learning_stats', {})
                
                message = "🤖 <b>СТАТУС СИСТЕМЫ</b>\n\n"
                message += f"✅ Модель: {'Обучена' if status_data.get('model_trained') else 'Не обучена'}\n"
                message += f"📊 Групп в датасете: {status_data.get('dataset_size', 0)}\n"
                message += f"🌐 Веб-версия: {'Запущена' if web_running else 'Не запущена'}\n"
                message += f"🔧 Автосервис: {'Активен' if auto_service_running else 'Остановлен'}\n"  # ← ИСПРАВЛЕНО
                message += f"🕐 Последний тираж: {current_draw}\n"
                
                # ✅ АНАЛИТИКА САМООБУЧЕНИЯ
                if learning_stats and 'message' not in learning_stats:
                    message += "\n📈 <b>АНАЛИТИКА САМООБУЧЕНИЯ:</b>\n"
                    message += f"🎯 Средняя точность: {learning_stats.get('recent_accuracy_avg', 0)*100:.1f}%\n"
                    message += f"📊 Проанализировано прогнозов: {learning_stats.get('total_predictions_analyzed', 0)}\n"
                    message += f"🏆 Лучшая точность: {learning_stats.get('best_accuracy', 0)*100:.1f}%\n"
                    message += f"📉 Худшая точность: {learning_stats.get('worst_accuracy', 0)*100:.1f}%\n"
                
                # Прогнозы
                predictions = status_data.get('last_predictions', [])
                if predictions:
                    message += "\n🔮 <b>ПОСЛЕДНИЕ ПРОГНОЗЫ:</b>\n"
                    for i, (group, score) in enumerate(predictions[:4], 1):
                        confidence = "🟢" if score > 0.02 else "🟡" if score > 0.01 else "🔴"
                        message += f"{i}. {group[0]} {group[1]} {group[2]} {group[3]} {confidence}\n"
                
                self.send_message(chat_id, message)
            else:
                self.send_message(chat_id, "❌ Сервис временно недоступен")
                    
        except Exception as e:  # ← ДОБАВИТЬ ЭТУ СТРОКУ
            logger.error(f"❌ Ошибка отправки статуса: {e}")
            self.send_message(chat_id, f"❌ Ошибка получения статуса: {e}")

    def is_auto_service_running(self):
        """Проверка, запущен ли автосервис"""
        try:
            result = subprocess.run(['pgrep', '-f', 'auto_learning_service.py --schedule'], 
                                capture_output=True, text=True)
            return result.returncode == 0
        except:
            return False

    def is_web_running(self):
        """Проверка, запущена ли веб-версия"""
        try:
            # Проверяем порт 8501 - самый надежный способ
            import socket
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(2)
            result = sock.connect_ex(('127.0.0.1', 8501))
            sock.close()
            
            is_running = (result == 0)
            logger.info(f"🌐 Проверка веб-версии (порт 8501): {'Запущена' if is_running else 'Не запущена'}")
            return is_running
            
        except Exception as e:
            logger.error(f"❌ Ошибка проверки веб-версии: {e}")
            return False

    def get_current_draw(self):
        """Получение актуального тиража из info.json"""
        try:
            info_path = '/opt/project/api_data/info.json'
            with open(info_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
            return data.get('current_draw', 'Нет данных')
        except:
            return 'Ошибка чтения'
      
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
