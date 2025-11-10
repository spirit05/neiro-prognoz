# services/telegram/utils.py
"""
Вспомогательные утилиты для Telegram бота - ПОЛНОСТЬЮ ОБНОВЛЕННЫЙ
"""

import logging
import subprocess
import socket
from typing import Dict, Any, Optional
from config.paths import INFO_FILE, SERVICE_STATE_FILE
from services.auto_learning.service import AutoLearningService
from ml.learning.self_learning import SelfLearningSystem
import json

logger = logging.getLogger('telegram_bot')

class SystemChecker:
    """Класс проверки состояния системы"""
    
    def __init__(self, auto_service: AutoLearningService = None):
        self.auto_service = auto_service
    
    def get_system_status(self) -> Dict[str, Any]:
        """Получение статуса системы с обработкой разных форматов данных"""
        try:
            status = {
                'service_active': False,
                'model_trained': False,
                'dataset_size': 0,
                'web_running': self.check_web_interface(),
                'learning_stats': {},
                'last_predictions': [],
                'last_processed_draw': 'Не обработан'
            }
            
            # 🔧 ИСПРАВЛЕНИЕ: Проверяем автосервис с безопасным обновлением
            if self.auto_service:
                try:
                    auto_status = self.auto_service.get_service_status()
                    if isinstance(auto_status, dict):
                        # Безопасное обновление только существующих ключей
                        for key in ['service_active', 'model_trained', 'dataset_size', 'last_processed_draw', 'consecutive_api_errors']:
                            if key in auto_status:
                                status[key] = auto_status[key]
                except Exception as e:
                    logger.warning(f"⚠️ Ошибка автосервиса: {e}")
            
            # 🔧 ИСПРАВЛЕНИЕ: Правильная обработка аналитики самообучения
            try:
                learning_system = SelfLearningSystem()
                learning_stats = learning_system.get_performance_stats()
                
                # Обрабатываем разные форматы данных
                if isinstance(learning_stats, list) and learning_stats:
                    # Берем последнюю запись и проверяем ее тип
                    last_stat = learning_stats[-1]
                    if isinstance(last_stat, dict):
                        status['learning_stats'] = last_stat
                    else:
                        # Если это не dict, создаем структурированные данные
                        status['learning_stats'] = {
                            'recent_data': last_stat,
                            'total_entries': len(learning_stats),
                            'message': 'Данные в формате списка'
                        }
                elif isinstance(learning_stats, dict):
                    status['learning_stats'] = learning_stats
                else:
                    status['learning_stats'] = {
                        'message': 'Нет данных для анализа',
                        'data_type': str(type(learning_stats)),
                        'data_sample': str(learning_stats)[:100] if learning_stats else 'Пусто'
                    }
                    
            except ImportError as e:
                logger.warning(f"⚠️ Система самообучения не доступна: {e}")
                status['learning_stats'] = {'message': 'Система самообучения не доступна'}
            except Exception as e:
                logger.error(f"❌ Ошибка получения аналитики обучения: {e}")
                status['learning_stats'] = {'message': f'Ошибка: {str(e)}'}
            
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
            return self._get_error_status(e)
    
    def _get_error_status(self, error: Exception) -> Dict[str, Any]:
        """Статус при ошибке"""
        return {
            'service_active': False,
            'model_trained': False, 
            'dataset_size': 0,
            'web_running': False,
            'learning_stats': {'message': f'Ошибка системы: {str(error)}'},
            'last_predictions': [],
            'error': True
        }
    
    def get_formatted_status(self) -> str:
        """Форматированный статус для Telegram"""
        status = self.get_system_status()
        
        # Эмодзи для статусов
        service_emoji = "🟢" if status.get('service_active') else "🔴"
        model_emoji = "✅" if status.get('model_trained') else "❌" 
        web_emoji = "🌐" if status.get('web_running') else "🔴"
        
        message = f"{service_emoji} <b>СТАТУС СИСТЕМЫ</b>\n\n"
        message += f"{service_emoji} Автосервис: {'АКТИВЕН' if status['service_active'] else 'ОСТАНОВЛЕН'}\n"
        message += f"{model_emoji} Модель: {'ОБУЧЕНА' if status['model_trained'] else 'НЕ ОБУЧЕНА'}\n"
        message += f"📊 Размер датасета: {status.get('dataset_size', 0)} групп\n"
        message += f"{web_emoji} Веб-интерфейс: {'ЗАПУЩЕН' if status['web_running'] else 'НЕ ЗАПУЩЕН'}\n"
        
        # Добавляем информацию о последнем тираже если есть
        last_draw = status.get('last_processed_draw')
        if last_draw and last_draw != 'Не обработан':
            message += f"🎯 Последний тираж: {last_draw}\n"
        
        # Добавляем аналитику самообучения если есть
        learning_stats = status.get('learning_stats', {})
        if learning_stats:
            if 'message' not in learning_stats:
                message += f"\n📈 <b>АНАЛИТИКА ОБУЧЕНИЯ</b>\n"
                # Пробуем разные возможные ключи для точности
                accuracy = (learning_stats.get('recent_accuracy_avg') or 
                          learning_stats.get('accuracy') or 
                          learning_stats.get('avg_accuracy'))
                if accuracy:
                    message += f"🎯 Средняя точность: {float(accuracy)*100:.1f}%\n"
                
                total_pred = (learning_stats.get('total_predictions_analyzed') or 
                            learning_stats.get('predictions_analyzed') or 
                            learning_stats.get('total_analyzed'))
                if total_pred:
                    message += f"📊 Проанализировано: {total_pred} прогнозов\n"
                
                # Показываем другие доступные метрики
                for key, value in learning_stats.items():
                    if key not in ['recent_accuracy_avg', 'total_predictions_analyzed', 'accuracy', 'avg_accuracy', 'predictions_analyzed']:
                        if isinstance(value, (int, float)) and key != 'total_entries':
                            message += f"📈 {key}: {value}\n"
            else:
                message += f"\n📊 Аналитика: {learning_stats['message']}\n"
        
        return message

    def is_auto_service_running(self) -> bool:
        """Проверка, запущен ли автосервис"""
        try:
            result = subprocess.run(['pgrep', '-f', 'auto_learning_service.py --schedule'], 
                                capture_output=True, text=True)
            return result.returncode == 0
        except Exception as e:
            logger.error(f"❌ Ошибка проверки автосервиса: {e}")
            return False
    
    def check_web_interface(self) -> bool:
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
