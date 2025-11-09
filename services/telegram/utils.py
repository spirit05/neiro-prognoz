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
    
    def get_system_status(self):
        """Получение статуса системы с обработкой разных форматов данных"""
        try:
            status = {
                'service_active': False,
                'model_trained': False,
                'dataset_size': 0,
                'web_running': self.check_web_interface(),
                'learning_stats': {},
                'last_predictions': []
            }
            
            # Проверяем автосервис
            try:
                from services.auto_learning.service import AutoLearningService
                auto_service = AutoLearningService()
                auto_status = auto_service.get_service_status()
                
                # 🔧 ИСПРАВЛЕНИЕ: Безопасное обновление статуса
                if isinstance(auto_status, dict):
                    status.update(auto_status)
            except ImportError as e:
                logger.warning(f"⚠️ Автосервис не доступен: {e}")
            
            # Получаем аналитику самообучения
            try:
                from ml.learning.self_learning import SelfLearningSystem
                learning_system = SelfLearningSystem()
                learning_stats = learning_system.get_performance_stats()
                
                # 🔧 ИСПРАВЛЕНИЕ: Проверяем тип learning_stats
                if isinstance(learning_stats, list):
                    if learning_stats:
                        status['learning_stats'] = learning_stats[-1]  # Берем последнюю запись
                    else:
                        status['learning_stats'] = {'message': 'Нет данных для анализа'}
                elif isinstance(learning_stats, dict):
                    status['learning_stats'] = learning_stats
                else:
                    status['learning_stats'] = {'message': 'Неизвестный формат данных'}
                    
            except ImportError as e:
                logger.warning(f"⚠️ Система самообучения не доступна: {e}")
                status['learning_stats'] = {'message': 'Система самообучения не доступна'}
            
            # Получаем последние прогнозы
            try:
                from ml.utils.data_utils import load_predictions
                predictions = load_predictions()
                if predictions and isinstance(predictions, list):
                    status['last_predictions'] = predictions[:4]
            except ImportError as e:
                logger.warning(f"⚠️ Не удалось загрузить прогнозы: {e}")
            
            return status
            
        except Exception as e:
            logger.error(f"❌ Ошибка загрузки аналитики: {e}")
            return {
                'service_active': False,
                'model_trained': False, 
                'dataset_size': 0,
                'web_running': False,
                'learning_stats': {'message': f'Ошибка: {str(e)}'},
                'last_predictions': []
            }
    
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
