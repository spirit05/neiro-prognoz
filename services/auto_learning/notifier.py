#!/usr/bin/env python3
"""
Telegram уведомления для автосервиса
"""

import os
import json
import requests
import time
import logging
from datetime import datetime
from typing import Dict, Any, Optional

logger = logging.getLogger('TelegramNotifier')

class TelegramNotifier:
    def __init__(self):
        self.config = self.load_config()
    
    def load_config(self) -> Dict[str, Any]:
        """Загрузка конфигурации Telegram"""
        try:
            config_path = os.path.join('/opt/dev', 'data', 'telegram_config.json')
            if os.path.exists(config_path):
                with open(config_path, 'r', encoding='utf-8') as f:
                    return json.load(f)
            return {'enabled': False}
        except Exception as e:
            logger.error(f"❌ Ошибка загрузки конфига Telegram: {e}")
            return {'enabled': False}
    
    def send_message(self, message: str, retry_critical: bool = False) -> bool:
        """Отправка сообщения в Telegram"""
        if not self.config.get('enabled', False):
            return False
        
        try:
            bot_token = self.config.get('bot_token')
            chat_id = self.config.get('chat_id')
            
            if not bot_token or not chat_id or bot_token == "YOUR_BOT_TOKEN_HERE":
                return False
            
            url = f"https://api.telegram.org/bot{bot_token}/sendMessage"
            payload = {
                'chat_id': chat_id,
                'text': message,
                'parse_mode': 'HTML'
            }
            
            # Для критических сообщений повторяем попытки
            max_attempts = 3 if retry_critical else 1
            for attempt in range(max_attempts):
                try:
                    response = requests.post(url, json=payload, timeout=10)
                    if response.status_code == 200:
                        logger.info("✅ Сообщение отправлено в Telegram")
                        return True
                    else:
                        logger.warning(f"⚠️ Ошибка Telegram API: {response.status_code}")
                except Exception as e:
                    logger.warning(f"⚠️ Ошибка отправки в Telegram (попытка {attempt + 1}): {e}")
                
                if attempt < max_attempts - 1:
                    time.sleep(5)
            
            return False
            
        except Exception as e:
            logger.error(f"❌ Критическая ошибка Telegram: {e}")
            return False
    
    def send_critical_error(self, draw: str, error_message: str, stacktrace: Optional[str] = None):
        """Отправка критической ошибки"""
        if not self.config.get('notifications', {}).get('critical_errors', False):
            return
        
        message = f"🔴 <b>КРИТИЧЕСКАЯ ОШИБКА</b>\n"
        message += f"📦 Тираж: {draw}\n"
        message += f"🕐 Время: {datetime.now().strftime('%H:%M:%S')}\n"
        message += f"❌ Ошибка: {error_message}\n"
        
        if stacktrace:
            message += f"\n<code>{stacktrace[:1000]}</code>"
        
        self.send_message(message, retry_critical=True)
    
    def send_service_stop(self, draw: str, reason: str):
        """Отправка уведомления об остановке сервиса"""
        if not self.config.get('notifications', {}).get('service_stop', False):
            return
        
        message = f"🛑 <b>ОСТАНОВКА СЕРВИСА</b>\n"
        message += f"📦 Тираж: {draw}\n"
        message += f"🕐 Время: {datetime.now().strftime('%H:%M:%S')}\n"
        message += f"📝 Причина: {reason}\n"
        message += f"🔧 Требуется ручной перезапуск"
        
        self.send_message(message, retry_critical=True)
    
    def send_predictions(self, predictions: list, draw: str):
        """Отправка прогнозов после дообучения"""
        if not self.config.get('notifications', {}).get('predictions', False):
            return
        
        message = f"🔮 <b>НОВЫЕ ПРОГНОЗЫ</b>\n"
        message += f"📦 После тиража: {draw}\n"
        message += f"🕐 Время: {datetime.now().strftime('%H:%M:%S')}\n\n"
        
        for i, (group, score) in enumerate(predictions[:4], 1):
            confidence = "🟢" if score > 0.02 else "🟡" if score > 0.01 else "🔴"
            message += f"{i}. {group[0]} {group[1]} {group[2]} {group[3]} ({score:.4f}) {confidence}\n"
        
        self.send_message(message)
    
    def process_status_command(self, status_data: Dict[str, Any]):
        """Обработка команды /status"""
        if not self.config.get('notifications', {}).get('status_command', False):
            return
        
        try:
            # Проверяем новые команды (простой polling)
            bot_token = self.config.get('bot_token')
            chat_id = self.config.get('chat_id')
            
            if not bot_token or not chat_id:
                return
            
            url = f"https://api.telegram.org/bot{bot_token}/getUpdates"
            response = requests.get(url, timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                if data.get('ok'):
                    for update in data.get('result', []):
                        message = update.get('message', {})
                        if message.get('text') == '/status':
                            # Отправляем статус
                            status_message = self.format_status_message(status_data)
                            self.send_message(status_message)
                            # Помечаем как обработанное
                            self.acknowledge_update(update['update_id'])
        except Exception as e:
            logger.warning(f"⚠️ Ошибка проверки команд Telegram: {e}")
    
    def format_status_message(self, status_data: Dict[str, Any]) -> str:
        """Форматирование сообщения статуса"""
        message = "🤖 <b>СТАТУС АВТОСЕРВИСА</b>\n\n"
        
        # Статус сервиса
        service_status = "✅ Активен" if status_data.get('service_active') else "🛑 Остановлен"
        message += f"{service_status}\n"
        
        # Модель
        model_status = "✅ Обучена" if status_data.get('model_trained') else "⚠️ Не обучена"
        message += f"🎯 Модель: {model_status}\n"
        
        # Последний тираж
        last_draw = status_data.get('last_processed_draw', 'Нет')
        message += f"🕐 Последний тираж: {last_draw}\n"
        
        return message
    
    def acknowledge_update(self, update_id: int):
        """Подтверждение обработки команды"""
        try:
            bot_token = self.config.get('bot_token')
            url = f"https://api.telegram.org/bot{bot_token}/getUpdates"
            requests.post(url, json={'offset': update_id + 1}, timeout=5)
        except:
            pass