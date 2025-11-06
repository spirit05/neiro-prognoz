from utils.logging_system import get_training_logger, get_ml_system_logger, get_auto_learning_logger
# services/auto_learning/service.py
"""
Основной сервис автообучения - ИСПРАВЛЕННАЯ ВЕРСИЯ
"""

import os
import sys
import time
import logging
from datetime import datetime

# Добавляем пути для импорта
PROJECT_ROOT = '/home/spirit/Desktop/project'
sys.path.insert(0, PROJECT_ROOT)
sys.path.insert(0, os.path.join(PROJECT_ROOT, 'services'))

from config.paths import SERVICE_STATE, INFO_JSON
from config.constants import MAX_CONSECUTIVE_ERRORS, Status, ServiceType
from .scheduler import SmartScheduler
from .api_client import APIClient
from .file_manager import load_json_safe, save_json_safe

# Настройка логирования
logger = get_AutoLearningService_logger()

# Пробуем импортировать TelegramNotifier
try:
    from services.telegram.notifier import TelegramNotifier
    TELEGRAM_AVAILABLE = True
    logger.info("✅ TelegramNotifier доступен")
except ImportError as e:
    TELEGRAM_AVAILABLE = False
    logger.warning(f"▲ TelegramNotifier недоступен: {e}")

class AutoLearningService:  # ← ИСПРАВЛЕНО ИМЯ КЛАССА
    def __init__(self):
        self.system = None

        # Инициализируем Telegram, если доступен
        if TELEGRAM_AVAILABLE:
            self.telegram = TelegramNotifier()
        else:
            self.telegram = None

        self.scheduler = SmartScheduler()
        self.api_client = APIClient()

        # ИСПРАВЛЕНО: Добавляем отсутствующие атрибуты
        self.service_active = True
        self.consecutive_api_errors = 0
        self.max_consecutive_errors = MAX_CONSECUTIVE_ERRORS  # ← ДОБАВЛЕНО
        self.last_processed_draw = None
        self._first_run = True  # ← ДОБАВЛЕНО

        self.initialize_system()
        self.load_service_state()

    def initialize_system(self):
        """Инициализация AI системы"""
        try:
            # Пробуем импортировать ML систему
            try:
                from ml.core.system import SimpleNeuralSystem
                self.system = SimpleNeuralSystem()
                
                def progress_callback(message):
                    logger.info(f"🔄 {message}")

                self.system.set_progress_callback(progress_callback)
                logger.info("✅ AI система инициализирована")
                return True
            except ImportError as e:
                logger.warning(f"▲ ML система недоступна: {e}")
                # Создаем заглушку для тестирования
                class MockSystem:
                    def __init__(self):
                        self.is_trained = True
                    def set_progress_callback(self, callback):
                        pass
                    def get_status(self):
                        return {'is_trained': True, 'dataset_size': 0}
                
                self.system = MockSystem()
                return True

        except Exception as e:
            logger.error(f"❌ Ошибка инициализации системы: {e}")
            return False

    def load_service_state(self):
        """Загрузка состояния сервиса"""
        try:
            state = load_json_safe(SERVICE_STATE)
            self.last_processed_draw = state.get('last_processed_draw')
            self.service_active = state.get('service_active', True)
            self.consecutive_api_errors = state.get('consecutive_api_errors', 0)

            logger.info(f"📦 Состояние сервиса загружено: активен={self.service_active}")
        except Exception as e:
            logger.warning(f"▲ Не удалось загрузить состояние сервиса: {e}")

    def save_service_state(self):
        """Сохранение состояния сервиса"""
        try:
            state = {
                'last_processed_draw': self.last_processed_draw,
                'service_active': self.service_active,
                'consecutive_api_errors': self.consecutive_api_errors,
                'last_update': datetime.now().isoformat()
            }
            save_json_safe(state, SERVICE_STATE)
        except Exception as e:
            logger.error(f"❌ Ошибка сохранения состояния сервиса: {e}")

    def process_new_group(self):
        """Основной метод обработки новой группы"""
        if not self.service_active:
            logger.info("⏸️ Сервис остановлен")
            return False

        logger.info("🔄 Запуск обработки новой группы...")

        try:
            # Шаг 1: Получаем новую группу через API
            result = self.api_client.call_api()

            if not result:
                self.consecutive_api_errors += 1
                self.save_service_state()

                if self.consecutive_api_errors >= self.max_consecutive_errors:
                    self.service_active = False
                    self.save_service_state()
                    logger.error("🚨 Достигнут максимум ошибок API. Останавливаем сервис.")
                    return False

            # Успешный запрос - сбрасываем счетчик ошибок
            self.consecutive_api_errors = 0
            self.save_service_state()

            logger.info("✅ API запрос успешен")
            return True

        except Exception as e:
            logger.error(f"❌ Критическая ошибка обработки: {e}")
            self.service_active = False
            self.save_service_state()
            return False

    def start_scheduled_service(self):
        """Запуск сервиса по расписанию"""
        if not self.service_active:
            logger.error("⏸️ Сервис остановлен из-за ошибок API.")
            return

        # Настройка адаптивного расписания
        success, schedule_type = self.scheduler.setup_adaptive_schedule(self.process_new_group)

        if not success:
            logger.error(f"❌ Не удалось настроить расписание: {schedule_type}")
            return

        logger.info(f"✅ Расписание настроено: {schedule_type}")

        try:
            while True:
                self.scheduler.run_pending()
                time.sleep(60)

        except KeyboardInterrupt:
            logger.info("🛑 Сервис остановлен пользователем")
        except Exception as e:
            logger.error(f"❌ Критическая ошибка в основном цикле: {e}")

    def get_service_status(self):
        """Получение статуса сервиса"""
        status = {
            'timestamp': datetime.now().isoformat(),
            'service_active': self.service_active,
            'system_initialized': self.system is not None,
            'last_processed_draw': self.last_processed_draw,
            'model_trained': self.system.is_trained if self.system else False,
            'consecutive_api_errors': self.consecutive_api_errors,
            'max_consecutive_errors': self.max_consecutive_errors,  # ← ТЕПЕРЬ ЕСТЬ!
            'service_type': ServiceType.AUTO_LEARNING,
            'telegram_available': TELEGRAM_AVAILABLE,
            'schedule_available': hasattr(self.scheduler, 'SCHEDULE_AVAILABLE') and self.scheduler.SCHEDULE_AVAILABLE
        }
        return status

    def manual_restart(self):
        """Ручной перезапуск сервиса"""
        if not self.service_active:
            logger.info("🔄 Ручной перезапуск сервиса...")
            self.service_active = True
            self.consecutive_api_errors = 0
            self._first_run = True
            self.save_service_state()
            return True
        else:
            logger.info("✅ Сервис уже активен")
            return False