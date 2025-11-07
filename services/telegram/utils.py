# services/telegram/utils.py
"""
Вспомогательные утилиты для Telegram бота
"""

import logging
import subprocess
import socket
from typing import Dict, Any  # ← ДОБАВЛЯЕМ ИМПОРТ
from config.paths import INFO_FILE, SERVICE_STATE_FILE
from services.auto_learning.service import AutoLearningService
from ml.learning.self_learning import SelfLearningSystem
import json

logger = logging.getLogger('telegram_bot')

class SystemChecker:
    """Класс проверки состояния системы"""
    
    def __init__(self, auto_service: AutoLearningService = None):
        self.auto_service = auto_service
    
    def get_system_status(self) -> str:
        """Получение полного статуса системы"""
        try:
            web_running = self.is_web_running()
            current_draw = self.get_current_draw()
            auto_service_running = self.is_auto_service_running()
            
            service_status = {}
            if self.auto_service:
                service_status = self.auto_service.get_service_status()
            
            learning_stats = {}
            try:
                learning_system = SelfLearningSystem()
                learning_stats = learning_system.get_performance_stats()
            except Exception as e:
                logger.error(f"❌ Ошибка загрузки аналитики: {e}")
                learning_stats = service_status.get('learning_stats', {})
            
            message = "🤖 <b>ПОЛНЫЙ СТАТУС СИСТЕМЫ</b>\n\n"
            
            message += f"🔧 Автосервис: {'🟢 АКТИВЕН' if service_status.get('service_active') else '🔴 ОСТАНОВЛЕН'}\n"
            message += f"🌐 Веб-версия: {'🟢 ЗАПУЩЕНА' if web_running else '🔴 НЕ ЗАПУЩЕНА'}\n"
            message += f"🤖 ML система: {'✅ Инициализирована' if service_status.get('system_initialized') else '❌ Не инициализирована'}\n"
            
            if service_status.get('model_trained'):
                message += f"🧠 Модель: ✅ Обучена\n"
                message += f"📊 Групп в датасете: {service_status.get('dataset_size', 0)}\n"
            else:
                message += f"🧠 Модель: ❌ Не обучена\n"
            
            message += f"🕐 Текущий тираж: {current_draw}\n"
            
            api_errors = service_status.get('consecutive_api_errors', 0)
            max_errors = service_status.get('max_consecutive_errors', 3)
            message += f"📡 Ошибок API: {api_errors}/{max_errors}\n"
            
            if learning_stats and 'message' not in learning_stats:
                message += "\n📈 <b>АНАЛИТИКА САМООБУЧЕНИЯ:</b>\n"
                message += f"🎯 Средняя точность: {learning_stats.get('recent_accuracy_avg', 0)*100:.1f}%\n"
                message += f"📊 Проанализировано прогнозов: {learning_stats.get('total_predictions_analyzed', 0)}\n"
                message += f"🏆 Лучшая точность: {learning_stats.get('best_accuracy', 0)*100:.1f}%\n"
                message += f"📉 Худшая точность: {learning_stats.get('worst_accuracy', 0)*100:.1f}%\n"
            
            if learning_stats and 'recommendations' in learning_stats:
                recs = learning_stats['recommendations']
                if recs and len(recs) > 0:
                    message += f"\n💡 <b>РЕКОМЕНДАЦИИ:</b>\n"
                    for rec in recs[:2]:
                        message += f"• {rec}\n"
            
            predictions = service_status.get('last_predictions', [])
            if predictions:
                message += "\n🔮 <b>ПОСЛЕДНИЕ ПРОГНОЗЫ:</b>\n"
                for i, (group, score) in enumerate(predictions[:4], 1):
                    confidence = "🟢" if score > 0.02 else "🟡" if score > 0.01 else "🔴"
                    message += f"{i}. {group[0]} {group[1]} {group[2]} {group[3]} {confidence}\n"
            
            return message
                    
        except Exception as e:
            logger.error(f"❌ Ошибка получения статуса системы: {e}")
            return f"❌ Ошибка получения статуса системы: {e}"
    
    def is_auto_service_running(self) -> bool:
        """Проверка, запущен ли автосервис"""
        try:
            result = subprocess.run(['pgrep', '-f', 'auto_learning_service.py --schedule'], 
                                capture_output=True, text=True)
            return result.returncode == 0
        except Exception as e:
            logger.error(f"❌ Ошибка проверки автосервиса: {e}")
            return False
    
    def is_web_running(self) -> bool:
        """Проверка, запущена ли веб-версия"""
        try:
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
    
    def get_current_draw(self) -> str:
        """Получение актуального тиража"""
        try:
            with open(INFO_FILE, 'r', encoding='utf-8') as f:
                data = json.load(f)
            return data.get('current_draw', 'Нет данных')
        except Exception as e:
            logger.error(f"❌ Ошибка чтения info.json: {e}")
            return 'Ошибка чтения'


class MessageSender:
    """Класс отправки сообщений в Telegram"""
    
    def __init__(self, bot_token: str):
        self.bot_token = bot_token
    
    def send_message(self, chat_id: int, text: str, parse_mode: str = 'HTML') -> bool:
        """Отправка сообщения в Telegram"""
        import requests
        
        try:
            url = f"https://api.telegram.org/bot{self.bot_token}/sendMessage"
            
            payload = {
                'chat_id': chat_id,
                'text': text,
                'parse_mode': parse_mode
            }
            
            response = requests.post(url, json=payload, timeout=10)
            if response.status_code == 200:
                logger.info(f"✅ Сообщение отправлено в чат {chat_id}")
                return True
            else:
                logger.error(f"❌ Ошибка отправки: {response.status_code} - {response.text}")
                return False
                
        except Exception as e:
            logger.error(f"❌ Ошибка отправки сообщения: {e}")
            return False
    
    def send_message_safe(self, chat_id: int, text: str, max_retries: int = 3) -> bool:
        """Безопасная отправка сообщения с повторными попытками"""
        for attempt in range(max_retries):
            if self.send_message(chat_id, text):
                return True
            logger.warning(f"⚠️ Повторная попытка отправки сообщения ({attempt + 1}/{max_retries})")
        
        logger.error(f"❌ Не удалось отправить сообщение после {max_retries} попыток")
        return False
