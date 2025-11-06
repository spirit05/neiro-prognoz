# services/telegram/notifier.py
"""
Telegram уведомления - РЕАЛЬНАЯ РЕАЛИЗАЦИЯ
"""

import requests
import json
import time
from datetime import datetime
from config.paths import TELEGRAM_CONFIG
from config.constants import TELEGRAM_TIMEOUT, TELEGRAM_MAX_ATTEMPTS
from config.logging_config import setup_logging

logger = setup_logging('TelegramNotifier')

class TelegramNotifier:
    def __init__(self):
        self.config = self._load_config()
        self.last_notification_time = {}
        self.notification_cooldown = 300  # 5 минут между одинаковыми уведомлениями

    def _load_config(self):
        """Загрузка конфигурации Telegram"""
        try:
            with open(TELEGRAM_CONFIG, 'r', encoding='utf-8') as f:
                config = json.load(f)
                
            if config.get('enabled', False):
                logger.info("✅ Telegram нотификатор активирован")
            else:
                logger.info("🔕 Telegram нотификатор отключен в конфигурации")
                
            return config
            
        except Exception as e:
            logger.error(f"❌ Ошибка загрузки конфига Telegram: {e}")
            return {'enabled': False}

    def send_message(self, message: str, message_type: str = "info", retry_critical: bool = False) -> bool:
        """Отправка сообщения в Telegram с улучшенной обработкой ошибок"""
        if not self.config.get('enabled', False):
            return False

        # Проверка кд для повторяющихся уведомлений
        if self._is_on_cooldown(message_type, message):
            logger.debug(f"🔕 Пропущено уведомление {message_type} (в режиме cooldown)")
            return True

        bot_token = self.config.get('bot_token')
        chat_id = self.config.get('chat_id')

        if not bot_token or not chat_id:
            logger.error("❌ Не настроен bot_token или chat_id для Telegram")
            return False

        try:
            url = f"https://api.telegram.org/bot{bot_token}/sendMessage"
            
            # Форматирование сообщения в зависимости от типа
            formatted_message = self._format_message(message, message_type)
            
            payload = {
                'chat_id': chat_id,
                'text': formatted_message,
                'parse_mode': 'HTML',
                'disable_web_page_preview': True
            }

            max_attempts = TELEGRAM_MAX_ATTEMPTS if retry_critical else 1

            for attempt in range(max_attempts):
                try:
                    response = requests.post(url, json=payload, timeout=TELEGRAM_TIMEOUT)
                    
                    if response.status_code == 200:
                        response_data = response.json()
                        if response_data.get('ok'):
                            logger.info(f"📨 Telegram уведомление отправлено: {message_type}")
                            self._update_cooldown(message_type, message)
                            return True
                        else:
                            logger.error(f"❌ Telegram API error: {response_data}")
                    else:
                        logger.error(f"❌ HTTP error {response.status_code}: {response.text}")

                    # Повторная попытка после задержки
                    if attempt < max_attempts - 1:
                        time.sleep(5 * (attempt + 1))  # Увеличивающаяся задержка

                except requests.exceptions.Timeout:
                    logger.warning(f"⏰ Таймаут при отправке Telegram сообщения (попытка {attempt + 1})")
                    if attempt < max_attempts - 1:
                        time.sleep(5)
                except requests.exceptions.ConnectionError as e:
                    logger.warning(f"🔌 Ошибка соединения Telegram (попытка {attempt + 1}): {e}")
                    if attempt < max_attempts - 1:
                        time.sleep(10)

            logger.error(f"❌ Не удалось отправить Telegram сообщение после {max_attempts} попыток")
            return False

        except Exception as e:
            logger.error(f"❌ Критическая ошибка отправки Telegram: {e}")
            return False

    def _format_message(self, message: str, message_type: str) -> str:
        """Форматирование сообщения для Telegram"""
        timestamp = datetime.now().strftime("%H:%M:%S")
        
        emoji_map = {
            'info': 'ℹ️',
            'warning': '⚠️',
            'error': '❌',
            'success': '✅',
            'critical': '🚨',
            'prediction': '🔮',
            'training': '🧠'
        }
        
        emoji = emoji_map.get(message_type, '📢')
        
        # Ограничение длины сообщения для Telegram (4096 символов)
        if len(message) > 4000:
            message = message[:4000] + "... [сообщение обрезано]"
            
        return f"{emoji} <b>[{timestamp}]</b>\n\n{message}"

    def send_predictions(self, predictions: list, draw: str, actual_group: tuple = None) -> bool:
        """Отправка прогнозов в Telegram"""
        if not predictions:
            return False

        message = f"🔮 <b>Прогнозы для тиража {draw}</b>\n\n"
        
        for i, (group, score) in enumerate(predictions[:5], 1):  # Топ-5 прогнозов
            message += f"{i}. <code>{group}</code> (вероятность: {score:.2%})\n"
            
        if actual_group:
            message += f"\n🎯 Фактический результат: <code>{actual_group}</code>"
            
        return self.send_message(message, "prediction")

    def send_system_status(self, status_data: dict) -> bool:
        """Отправка статуса системы в Telegram"""
        message = self.format_status_message(status_data)
        return self.send_message(message, "info")

    def format_status_message(self, status_data: dict) -> str:
        """Форматирование сообщения статуса системы"""
        message = "📊 <b>Статус системы</b>\n\n"
        
        # Основная информация
        service_status = "✅ Активен" if status_data.get('service_active') else "⏸️ Остановлен"
        message += f"• Сервис: {service_status}\n"
        
        model_status = "✅ Обучена" if status_data.get('model_trained') else "❌ Не обучена"
        message += f"• Модель: {model_status}\n"
        
        message += f"• Ошибок API подряд: {status_data.get('consecutive_api_errors', 0)}\n"
        
        if status_data.get('last_processed_draw'):
            message += f"• Последний тираж: {status_data.get('last_processed_draw')}\n"
            
        # Дополнительная информация
        if status_data.get('learning_stats'):
            stats = status_data['learning_stats']
            accuracy = stats.get('recent_accuracy_avg', 0)
            message += f"• Точность предсказаний: {accuracy:.1%}\n"
            
        message += f"\n🕒 {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
        
        return message

    def _is_on_cooldown(self, message_type: str, message: str) -> bool:
        """Проверка, находится ли уведомление в режиме cooldown"""
        key = f"{message_type}_{hash(message) % 10000}"  # Упрощенный хэш для экономии памяти
        
        if key in self.last_notification_time:
            elapsed = time.time() - self.last_notification_time[key]
            return elapsed < self.notification_cooldown
            
        return False

    def _update_cooldown(self, message_type: str, message: str):
        """Обновление времени последнего уведомления"""
        key = f"{message_type}_{hash(message) % 10000}"
        self.last_notification_time[key] = time.time()
        
        # Очистка старых записей (больше 1000)
        if len(self.last_notification_time) > 1000:
            # Оставляем только последние 500 записей
            keys_to_remove = list(self.last_notification_time.keys())[:-500]
            for k in keys_to_remove:
                del self.last_notification_time[k]
