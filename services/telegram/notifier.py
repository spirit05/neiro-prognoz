# services/telegram/notifier.py
"""
Telegram уведомления
"""
import requests
import json
import time
from datetime import datetime
from config.paths import TELEGRAM_CONFIG
from config.constants import TELEGRAM_TIMEOUT, TELEGRAM_MAX_ATTEMPTS

class TelegramNotifier:
    def __init__(self):
        self.config = self.load_config()
    
    def load_config(self):
        """Загрузка конфигурации Telegram"""
        try:
            import json
            with open(TELEGRAM_CONFIG, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception as e:
            print(f"❌ Ошибка загрузки конфига Telegram: {e}")
            return {'enabled': False}
    
    def send_message(self, message, retry_critical=False):
        """Отправка сообщения в Telegram"""
        if not self.config.get('enabled', False):
            return False
        
        try:
            bot_token = self.config.get('bot_token')
            chat_id = self.config.get('chat_id')
            
            if not bot_token or not chat_id:
                return False
            
            url = f"https://api.telegram.org/bot{bot_token}/sendMessage"
            payload = {
                'chat_id': chat_id,
                'text': message,
                'parse_mode': 'HTML'
            }
            
            max_attempts = TELEGRAM_MAX_ATTEMPTS if retry_critical else 1
            
            for attempt in range(max_attempts):
                try:
                    response = requests.post(url, json=payload, timeout=TELEGRAM_TIMEOUT)
                    if response.status_code == 200:
                        return True
                except Exception as e:
                    if attempt < max_attempts - 1:
                        time.sleep(5)
            
            return False
            
        except Exception as e:
            print(f"❌ Критическая ошибка Telegram: {e}")
            return False
    
    def format_status_message(self, status_data):
        """Форматирование сообщения статуса"""
        message = "🤖 <b>СТАТУС АВТОСЕРВИСА</b>\n\n"
        
        service_status = "✅ Активен" if status_data.get('service_active') else "🛑 Остановлен"
        message += f"{service_status}\n"
        
        model_status = "✅ Обучена" if status_data.get('model_trained') else "⚠️ Не обучена"
        message += f"🎯 Модель: {model_status}\n"
        
        message += f"📊 Ошибок API подряд: {status_data.get('consecutive_api_errors', 0)}\n"
        message += f"🕐 Последний тираж: {status_data.get('last_processed_draw', 'Нет')}\n"
        
        return message