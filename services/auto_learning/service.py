#!/usr/bin/env python3
"""
Автономный сервис для автоматического получения данных и дообучения
С УМНЫМ РАСПИСАНИЕМ И TELEGRAM УВЕДОМЛЕНИЯМИ
Рефакторинг для новой структуры проекта
"""

import os
import sys
import time
import json
import logging
import schedule
from datetime import datetime, timedelta

# Добавляем пути для импорта
PROJECT_ROOT = '/opt/dev'
sys.path.insert(0, PROJECT_ROOT)
sys.path.insert(0, os.path.join(PROJECT_ROOT, 'ml'))

# Импорты из новой структуры
from services.auto_learning.api_client import APIClient
from services.auto_learning.scheduler import SmartScheduler
from services.auto_learning.file_manager import FileLock, safe_file_operation
from services.auto_learning.state_manager import StateManager
from services.auto_learning.notifier import TelegramNotifier

# Настройка логирования
logger = logging.getLogger('AutoLearningService')

# Константы
MAX_API_RETRIES = 3
API_RETRY_DELAY = 30
SERVICE_STATE_FILE = os.path.join(PROJECT_ROOT, 'data', 'service_state.json')

class AutoLearningService:
    def __init__(self):
        self.system = None
        self.api_client = APIClient()
        self.scheduler = SmartScheduler()
        self.state_manager = StateManager()
        self.telegram = TelegramNotifier()
        self.service_active = True
        
        self.initialize_system()
        self.load_service_state()
    
    def initialize_system(self):
        """Инициализация AI системы"""
        try:
            # Импортируем из новой структуры ML системы
            from ml.core.predictor import EnhancedPredictor
            from ml.learning.self_learning import SelfLearningSystem
            
            # TODO: Заменить на актуальную инициализацию ML системы
            # Временная заглушка - будет обновлена после интеграции
            self.system = type('MockSystem', (), {
                'is_trained': True,
                'add_data_and_retrain': lambda x, **kwargs: self.mock_retrain(x),
                'get_status': lambda: {'status': 'mock'},
                'get_learning_insights': lambda: {}
            })()
            
            logger.info("✅ AI система инициализирована")
            return True
        except Exception as e:
            logger.error(f"❌ Ошибка инициализации системы: {e}")
            return False
    
    def mock_retrain(self, combination):
        """Временная заглушка для дообучения"""
        logger.info(f"🧠 Мок дообучение на данных: {combination}")
        # Возвращаем mock прогнозы
        return [
            ((1, 2, 3, 4), 0.15),
            ((5, 6, 7, 8), 0.12),
            ((9, 10, 11, 12), 0.10),
            ((13, 14, 15, 16), 0.08)
        ]
    
    def load_service_state(self):
        """Загрузка состояния сервиса"""
        try:
            state = self.state_manager.load_state()
            if state:
                self.service_active = state.get('service_active', True)
                logger.info(f"📦 Состояние сервиса загружено: активен={self.service_active}")
        except Exception as e:
            logger.warning(f"⚠️ Не удалось загрузить состояние сервиса: {e}")
    
    def save_service_state(self):
        """Сохранение состояния сервиса"""
        try:
            state = {
                'service_active': self.service_active,
                'last_update': datetime.now().isoformat()
            }
            self.state_manager.save_state(state)
        except Exception as e:
            logger.error(f"❌ Ошибка сохранения состояния сервиса: {e}")
    
    def process_new_group(self):
        """Основной метод обработки новой группы"""
        if not self.service_active:
            logger.info("⏸️ Сервис остановлен из-за ошибок API. Требуется ручной перезапуск.")
            return False
        
        logger.info("🔄 Запуск обработки новой группы...")
        
        try:
            # Шаг 1: Получаем новую группу через API
            result = self.api_client.get_data_with_retries()
            
            if not result:
                logger.error("❌ Не удалось получить данные от API")
                return False
            
            # Шаг 2: Получаем информацию о текущем состоянии
            current_info = self.api_client.get_current_info()
            if not current_info:
                logger.error("❌ Не удалось получить текущую информацию")
                return False
            
            # Шаг 3: Находим последнюю необработанную запись
            last_unprocessed = self.api_client.get_last_unprocessed_entry()
            if not last_unprocessed:
                logger.info("📝 Нет необработанных записей")
                return True
            
            processing_draw = last_unprocessed.get('draw')
            new_combination = last_unprocessed.get('combination')
            
            logger.info(f"🎯 Обработка тиража {processing_draw}: {new_combination}")
            
            # Шаг 4: Проверяем валидность группы
            from ml.core.data_processor import DataProcessor
            if not DataProcessor.validate_group(new_combination):
                logger.error(f"❌ Невалидная группа: {new_combination}")
                return False
            
            # Шаг 5: Сравниваем с предыдущими прогнозами
            comparison_result = self.compare_with_predictions(new_combination)
            
            # Шаг 6: Добавляем данные и дообучаем модель
            learning_result = self.add_data_and_retrain(new_combination)
            
            # Шаг 7: Помечаем как обработанную
            self.api_client.mark_entry_processed(processing_draw)
            
            # Шаг 8: Сохраняем результат
            result_data = {
                'timestamp': datetime.now().isoformat(),
                'draw': processing_draw,
                'combination': new_combination,
                'comparison': comparison_result,
                'learning_success': bool(learning_result),
                'new_predictions_count': len(learning_result) if learning_result else 0,
                'service_type': 'auto_learning'
            }
            
            self.save_learning_result(result_data)
            self.save_service_state()
            
            # Шаг 9: Отправляем прогнозы если включено
            if learning_result:
                self.telegram.send_predictions(learning_result, processing_draw)
            
            logger.info(f"✅ Обработка завершена! Новых прогнозов: {len(learning_result) if learning_result else 0}")
            
            return True
            
        except Exception as e:
            logger.error(f"❌ Критическая ошибка обработки новой группы: {e}")
            
            # Отправляем критическую ошибку в Telegram
            import traceback
            current_info = self.api_client.get_current_info()
            current_draw = current_info.get('current_draw', 'unknown')
            self.telegram.send_critical_error(current_draw, str(e), traceback.format_exc())
            
            # Останавливаем сервис
            self.service_active = False
            self.save_service_state()
            self.telegram.send_service_stop(current_draw, f"Критическая ошибка: {str(e)}")
            
            return False
    
    def compare_with_predictions(self, new_combination: str):
        """Сравнение новой группы с предыдущими прогнозами"""
        try:
            # TODO: Реализовать после интеграции с ML системой
            logger.info(f"🔍 Сравнение новой группы с прогнозами: {new_combination}")
            return {'matches_found': 0}
            
        except Exception as e:
            logger.error(f"❌ Ошибка сравнения с прогнозами: {e}")
            return {'matches_found': 0, 'error': str(e)}
    
    def add_data_and_retrain(self, new_combination: str):
        """Добавление данных и дообучение модели"""
        try:
            logger.info("🧠 Добавление данных и дообучение модели...")
            
            # Используем ML систему для дообучения
            predictions = self.system.add_data_and_retrain(new_combination, retrain_epochs=3)
            
            if predictions:
                logger.info(f"✅ Дообучение завершено. Сгенерировано {len(predictions)} прогнозов")
                return predictions
            else:
                logger.warning("⚠️ Дообучение завершено, но прогнозы не сгенерированы")
                return []
                
        except Exception as e:
            logger.error(f"❌ Ошибка дообучения: {e}")
            return []
    
    def save_learning_result(self, result_data):
        """Сохранение результата обучения"""
        try:
            result_path = os.path.join(PROJECT_ROOT, 'data', 'learning_results.json')
            
            def save_operation(filename, data):
                all_results = []
                if os.path.exists(filename):
                    with open(filename, 'r', encoding='utf-8') as f:
                        all_results = json.load(f)
                
                all_results.append(data)
                
                if len(all_results) > 100:
                    all_results = all_results[-100:]
                
                with open(filename, 'w', encoding='utf-8') as f:
                    json.dump(all_results, f, ensure_ascii=False, indent=2)
            
            safe_file_operation(save_operation, result_path, result_data)
            logger.info("💾 Результат обучения сохранен")
            
        except Exception as e:
            logger.error(f"❌ Ошибка сохранения результата обучения: {e}")
    
    def get_service_status(self):
        """Получение статуса сервиса"""
        status = {
            'timestamp': datetime.now().isoformat(),
            'service_active': self.service_active,
            'system_initialized': self.system is not None,
            'model_trained': self.system.is_trained if self.system else False,
            'service_type': 'auto_learning'
        }
        
        if self.system:
            try:
                system_status = self.system.get_status()
                status.update(system_status)
            except Exception as e:
                status['system_status_error'] = str(e)
        
        return status
    
    def manual_restart(self):
        """Ручной перезапуск сервиса после остановки"""
        if not self.service_active:
            logger.info("🔄 Ручной перезапуск сервиса...")
            self.service_active = True
            self.save_service_state()
            
            # Telegram уведомление о перезапуске
            self.telegram.send_message("✅ <b>СЕРВИС ПЕРЕЗАПУЩЕН</b>\nСервис автообучения снова активен")
            
            return True
        else:
            logger.info("✅ Сервис уже активен")
            return False
    
    def run_once(self):
        """Однократный запуск обработки"""
        if not self.service_active:
            logger.warning("⏸️ Сервис остановлен. Используйте --force для принудительного запуска.")
            return False
        
        logger.info("🚀 Запуск однократной обработки...")
        
        success = self.process_new_group()
        
        if success:
            next_interval = self.scheduler.calculate_next_run_time()
            logger.info(f"⏰ Следующий запрос через {next_interval:.1f} минут")
        
        return success
    
    def start_scheduled_service(self):
        """Запуск сервиса по расписанию"""
        if not self.service_active:
            logger.error("🚨 Сервис остановлен из-за ошибок API. Запуск по расписанию отменен.")
            logger.info("💡 Используйте: python3 service.py --restart")
            return
        
        logger.info("⏰ Запуск сервиса по расписанию")
        
        # Рассчитываем первый интервал
        first_interval = self.scheduler.calculate_next_run_time()
        logger.info(f"⏰ Первый запрос через {first_interval:.1f} минут")
        
        # Настраиваем расписание
        schedule.every(15).minutes.do(self.safe_scheduled_task)
        
        # Запускаем сразу при старте
        self.safe_scheduled_task()
        
        logger.info("✅ Сервис запущен. Ожидание следующего запуска...")
        
        try:
            while True:
                # Проверяем команды Telegram
                status_data = self.get_service_status()
                self.telegram.process_status_command(status_data)
                
                schedule.run_pending()
                time.sleep(60)  # Проверяем каждую минуту
                
        except KeyboardInterrupt:
            logger.info("🛑 Сервис остановлен пользователем")
        except Exception as e:
            logger.error(f"❌ Критическая ошибка в основном цикле сервиса: {e}")
    
    def safe_scheduled_task(self):
        """Безопасное выполнение запланированной задачи"""
        if not self.service_active:
            return
        
        try:
            logger.info("🔔 Выполнение запланированной задачи...")
            self.process_new_group()
        except Exception as e:
            logger.error(f"❌ Ошибка в запланированной задаче: {e}")

if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description='Auto Learning Service')
    parser.add_argument('--once', action='store_true', help='Run once and exit')
    parser.add_argument('--schedule', action='store_true', help='Run on schedule (every 15 minutes)')
    parser.add_argument('--restart', action='store_true', help='Manual restart after API errors')
    parser.add_argument('--status', action='store_true', help='Show service status')
    parser.add_argument('--force', action='store_true', help='Force run once even if service is stopped')
    parser.add_argument('--test-telegram', action='store_true', help='Test Telegram notifications')
    
    args = parser.parse_args()
    
    service = AutoLearningService()
    
    if not service.system:
        logger.error("❌ Не удалось инициализировать систему. Выход.")
        sys.exit(1)
    
    if args.test_telegram:
        print("🧪 Тестирование Telegram уведомлений...")
        service.telegram.send_message("🧪 <b>ТЕСТОВОЕ УВЕДОМЛЕНИЕ</b>\nЭто тестовое сообщение от автосервиса")
        sys.exit(0)
    
    if args.status:
        status = service.get_service_status()
        print(json.dumps(status, indent=2, ensure_ascii=False))
        sys.exit(0)
    
    if args.restart:
        if service.manual_restart():
            print("✅ Сервис перезапущен")
        else:
            print("✅ Сервис уже активен")
        sys.exit(0)
    
    if args.force:
        service.service_active = True
    
    if args.once:
        success = service.run_once()
        sys.exit(0 if success else 1)
    elif args.schedule:
        service.start_scheduled_service()
    else:
        # По умолчанию показываем статус
        status = service.get_service_status()
        print(json.dumps(status, indent=2, ensure_ascii=False))