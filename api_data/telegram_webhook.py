# api_data/telegram_webhook.py
#!/usr/bin/env python3
"""
Веб-сервер для Telegram вебхука
"""

import os
import sys
import logging
from flask import Flask, request, jsonify
import threading
import time

# Добавляем пути
PROJECT_PATH = '/opt/project'
sys.path.insert(0, PROJECT_PATH)
sys.path.insert(0, os.path.dirname(__file__))

# Настройка логирования
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger('TelegramWebhook')

app = Flask(__name__)

# Глобальная переменная для сервиса
auto_service = None

def init_auto_service():
    """Инициализация автосервиса в отдельном потоке"""
    global auto_service
    try:
        from auto_learning_service import AutoLearningService
        auto_service = AutoLearningService()
        logger.info("✅ Автосервис инициализирован для вебхука")
    except Exception as e:
        logger.error(f"❌ Ошибка инициализации автосервиса: {e}")

@app.route('/webhook/telegram', methods=['POST'])
def telegram_webhook():
    """Обработчик вебхука от Telegram"""
    try:
        update = request.get_json()
        logger.info(f"📨 Получено сообщение от Telegram: {update}")
        
        if 'message' in update:
            message = update['message']
            text = message.get('text', '').strip()
            chat_id = message['chat']['id']
            
            if text == '/start':
                response = "🤖 <b>Добро пожаловать в AI Prediction System!</b>\n\n" \
                          "Доступные команды:\n" \
                          "/status - статус системы\n" \
                          "/help - помощь\n" \
                          "/predictions - последние прогнозы"
                send_telegram_message(chat_id, response)
                
            elif text == '/status':
                send_system_status(chat_id)
                
            elif text == '/predictions':
                send_last_predictions(chat_id)
                
            elif text == '/help':
                response = "🆘 <b>Помощь по командам:</b>\n\n" \
                          "/status - полный статус системы\n" \
                          "/predictions - последние 4 прогноза\n" \
                          "/help - эта справка"
                send_telegram_message(chat_id, response)
                
            else:
                response = "❌ Неизвестная команда. Используйте /help для списка команд"
                send_telegram_message(chat_id, response)
        
        return jsonify({'status': 'ok'})
        
    except Exception as e:
        logger.error(f"❌ Ошибка обработки вебхука: {e}")
        return jsonify({'status': 'error', 'message': str(e)})

def send_telegram_message(chat_id, text):
    """Отправка сообщения в Telegram"""
    try:
        from auto_learning_service import TelegramNotifier
        notifier = TelegramNotifier()
        
        # Используем существующий метод отправки
        notifier.config['chat_id'] = str(chat_id)
        success = notifier.send_message(text)
        
        if success:
            logger.info(f"✅ Сообщение отправлено в чат {chat_id}")
        else:
            logger.error(f"❌ Не удалось отправить сообщение в чат {chat_id}")
            
    except Exception as e:
        logger.error(f"❌ Ошибка отправки сообщения: {e}")

def send_system_status(chat_id):
    """Отправка статуса системы"""
    try:
        if auto_service:
            status_data = auto_service.get_service_status()
            from auto_learning_service import TelegramNotifier
            notifier = TelegramNotifier()
            notifier.config['chat_id'] = str(chat_id)
            
            status_message = notifier.format_status_message(status_data)
            notifier.send_message(status_message)
            logger.info(f"✅ Статус системы отправлен в чат {chat_id}")
        else:
            send_telegram_message(chat_id, "❌ Сервис временно недоступен")
            
    except Exception as e:
        logger.error(f"❌ Ошибка отправки статуса: {e}")
        send_telegram_message(chat_id, f"❌ Ошибка получения статуса: {e}")

def send_last_predictions(chat_id):
    """Отправка последних прогнозов"""
    try:
        from model.data_loader import load_predictions
        predictions = load_predictions()
        
        if predictions:
            message = "🔮 <b>ПОСЛЕДНИЕ ПРОГНОЗЫ</b>\n\n"
            for i, (group, score) in enumerate(predictions[:4], 1):
                confidence = "🟢" if score > 0.02 else "🟡" if score > 0.01 else "🔴"
                message += f"{i}. {group[0]} {group[1]} {group[2]} {group[3]} ({score:.4f}) {confidence}\n"
        else:
            message = "📝 Прогнозы еще не сгенерированы"
            
        send_telegram_message(chat_id, message)
        
    except Exception as e:
        logger.error(f"❌ Ошибка отправки прогнозов: {e}")
        send_telegram_message(chat_id, f"❌ Ошибка получения прогнозов: {e}")

def setup_webhook():
    """Настройка вебхука в Telegram"""
    try:
        from auto_learning_service import TelegramNotifier
        notifier = TelegramNotifier()
        
        if not notifier.config.get('enabled', False):
            logger.error("❌ Telegram не настроен в конфиге")
            return False
        
        bot_token = notifier.config.get('bot_token')
        webhook_url = f"https://spirit3105.fvds.ru/webhook/telegram"
        
        import requests
        response = requests.post(
            f"https://api.telegram.org/bot{bot_token}/setWebhook",
            json={'url': webhook_url}
        )
        
        if response.status_code == 200:
            logger.info(f"✅ Вебхук установлен: {webhook_url}")
            return True
        else:
            logger.error(f"❌ Ошибка установки вебхука: {response.text}")
            return False
            
    except Exception as e:
        logger.error(f"❌ Ошибка настройки вебхука: {e}")
        return False

if __name__ == "__main__":
    # Инициализируем сервис в фоне
    init_thread = threading.Thread(target=init_auto_service, daemon=True)
    init_thread.start()
    
    # Настраиваем вебхук
    if setup_webhook():
        logger.info("🚀 Запуск веб-сервера на порту 5000...")
        app.run(host='0.0.0.0', port=5000, debug=False)
    else:
        logger.error("❌ Не удалось настроить вебхук")