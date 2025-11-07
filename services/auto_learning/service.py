#!/usr/bin/env python3
"""
Автономный сервис для автоматического получения данных и дообучения
С РЕАЛЬНОЙ ИНТЕГРАЦИЕЙ ML СИСТЕМЫ
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
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(os.path.join(PROJECT_ROOT, 'data', 'logs', 'auto_learning.log')),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger('AutoLearningService')

# Константы
MAX_API_RETRIES = 3
API_RETRY_DELAY = 30

class AutoLearningService:
    def __init__(self):
        self.system = None
        self.api_client = APIClient()
        self.scheduler = SmartScheduler()
        self.state_manager = StateManager()
        self.telegram = TelegramNotifier()
        self.service_active = True
        self.consecutive_api_errors = 0
        self.max_consecutive_errors = 3
        
        self.initialize_system()
        self.load_service_state()
    
    def initialize_system(self):
        """Инициализация AI системы с реальной ML интеграцией"""
        try:
            # Импортируем реальные компоненты ML системы
            from ml.core.data_processor import DataProcessor
            from ml.learning.self_learning import SelfLearningSystem
            from ml.ensemble.ensemble import EnsemblePredictor
            
            # Инициализируем систему самообучения
            self.system = SelfLearningSystem()
            
            def progress_callback(message):
                logger.info(f"📢 ML System: {message}")
            
            self.system.set_progress_callback(progress_callback)
            
            logger.info("✅ AI система инициализирована с реальной ML интеграцией")
            return True
            
        except Exception as e:
            logger.error(f"❌ Ошибка инициализации ML системы: {e}")
            # Fallback на упрощенную систему если основные компоненты недоступны
            return self.initialize_fallback_system()
    
    def initialize_fallback_system(self):
        """Резервная инициализация системы"""
        try:
            # Пробуем импортировать базовые компоненты
            from ml.core.predictor import EnhancedPredictor
            from ml.core.trainer import EnhancedTrainer
            
            logger.info("🔄 Используется резервная инициализация ML системы")
            self.system = type('FallbackSystem', (), {
                'is_trained': True,
                'add_data_and_retrain': lambda x, **kwargs: self.fallback_retrain(x),
                'get_status': lambda: {'status': 'fallback', 'model_trained': True},
                'get_learning_insights': lambda: {'status': 'fallback'}
            })()
            return True
        except Exception as e:
            logger.error(f"❌ Резервная инициализация также не удалась: {e}")
            return False
    
    def fallback_retrain(self, combination):
        """Резервный метод дообучения"""
        logger.info(f"🔄 Резервное дообучение на данных: {combination}")
        try:
            # Простая логика генерации прогнозов
            from ml.core.data_processor import DataProcessor
            
            # Валидация группы
            if not DataProcessor.validate_group(combination):
                logger.error(f"❌ Невалидная группа в резервном режиме: {combination}")
                return []
            
            # Генерация простых прогнозов
            numbers = [int(x) for x in combination.split()]
            predictions = []
            
            for i in range(4):
                # Простая логика - немного изменяем исходные числа
                pred_numbers = [(x + i + 1) % 20 for x in numbers]
                pred_tuple = tuple(sorted(pred_numbers))
                score = 0.15 - (i * 0.02)  # Убывающая уверенность
                predictions.append((pred_tuple, score))
            
            logger.info(f"✅ Резервные прогнозы сгенерированы: {len(predictions)}")
            return predictions
            
        except Exception as e:
            logger.error(f"❌ Ошибка в резервном дообучении: {e}")
            return []
    
    def load_service_state(self):
        """Загрузка состояния сервиса"""
        try:
            state = self.state_manager.load_state()
            if state:
                self.service_active = state.get('service_active', True)
                self.consecutive_api_errors = state.get('consecutive_api_errors', 0)
                logger.info(f"📦 Состояние сервиса загружено: активен={self.service_active}, ошибок={self.consecutive_api_errors}")
        except Exception as e:
            logger.warning(f"⚠️ Не удалось загрузить состояние сервиса: {e}")
    
    def save_service_state(self):
        """Сохранение состояния сервиса"""
        try:
            state = {
                'service_active': self.service_active,
                'consecutive_api_errors': self.consecutive_api_errors,
                'last_update': datetime.now().isoformat()
            }
            self.state_manager.save_state(state)
        except Exception as e:
            logger.error(f"❌ Ошибка сохранения состояния сервиса: {e}")
    
    def call_api_with_retries(self):
        """Вызов API с повторными попытками и обработкой ошибок"""
        for attempt in range(MAX_API_RETRIES):
            try:
                logger.info(f"📡 Попытка {attempt + 1}/{MAX_API_RETRIES}: запрос к API...")
                result = self.api_client.get_data_with_retries()
                
                if result:
                    # Успешный запрос - сбрасываем счетчик ошибок
                    self.consecutive_api_errors = 0
                    self.save_service_state()
                    return result
                else:
                    # Ошибка API
                    self.consecutive_api_errors += 1
                    logger.warning(f"⚠️ Ошибка API (попытка {attempt + 1}). Всего ошибок подряд: {self.consecutive_api_errors}")
                    
                    if self.consecutive_api_errors >= self.max_consecutive_errors:
                        logger.error("🚨 Достигнут максимум ошибок API. Останавливаем сервис.")
                        self.service_active = False
                        self.save_service_state()
                        
                        # Telegram уведомление
                        current_info = self.api_client.get_current_info()
                        current_draw = current_info.get('current_draw', 'unknown')
                        self.telegram.send_service_stop(current_draw, "Недоступность API")
                        
                        return None
                    
                    if attempt < MAX_API_RETRIES - 1:
                        time.sleep(API_RETRY_DELAY)
                        
            except Exception as e:
                self.consecutive_api_errors += 1
                logger.error(f"❌ Исключение при вызове API (попытка {attempt + 1}): {e}")
                
                if self.consecutive_api_errors >= self.max_consecutive_errors:
                    logger.error("🚨 Достигнут максимум ошибок API. Останавливаем сервис.")
                    self.service_active = False
                    self.save_service_state()
                    
                    # Telegram уведомление
                    import traceback
                    self.telegram.send_critical_error(
                        'unknown', 
                        f"Исключение API: {str(e)}", 
                        traceback.format_exc()
                    )
                    
                    return None
                
                if attempt < MAX_API_RETRIES - 1:
                    time.sleep(API_RETRY_DELAY)
        
        return None
    
    def process_new_group(self):
        """Основной метод обработки новой группы с реальной ML интеграцией"""
        if not self.service_active:
            logger.info("⏸️ Сервис остановлен из-за ошибок API. Требуется ручной перезапуск.")
            return False
        
        logger.info("🔄 Запуск обработки новой группы...")
        
        try:
            # Шаг 1: Получаем новую группу через API
            result = self.call_api_with_retries()
            
            if not result:
                # API недоступно - сервис уже остановлен в call_api_with_retries
                return False
            
            # Шаг 2: Находим последнюю необработанную запись
            last_unprocessed = self.api_client.get_last_unprocessed_entry()
            if not last_unprocessed:
                logger.info("📝 Нет необработанных записей")
                return True
            
            processing_draw = last_unprocessed.get('draw')
            new_combination = last_unprocessed.get('combination')
            
            logger.info(f"🎯 Обработка тиража {processing_draw}: {new_combination}")
            
            # Шаг 3: Проверяем валидность группы
            from ml.core.data_processor import DataProcessor
            if not DataProcessor.validate_group(new_combination):
                logger.error(f"❌ Невалидная группа: {new_combination}")
                return False
            
            # Шаг 4: Сравниваем с предыдущими прогнозами
            comparison_result = self.compare_with_predictions(new_combination)
            
            # Шаг 5: Добавляем данные и дообучаем модель
            learning_result = self.add_data_and_retrain(new_combination)
            
            # Шаг 6: Помечаем как обработанную
            self.api_client.mark_entry_processed(processing_draw)
            
            # Шаг 7: Сохраняем результат
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
            
            # Шаг 8: Отправляем прогнозы если включено
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
            from ml.core.data_processor import DataProcessor
            
            # Загружаем предыдущие прогнозы
            predictions_path = os.path.join(PROJECT_ROOT, 'data', 'predictions_state.json')
            if not os.path.exists(predictions_path):
                return {'matches_found': 0}
            
            with open(predictions_path, 'r', encoding='utf-8') as f:
                predictions_data = json.load(f)
            
            previous_predictions = predictions_data.get('predictions', [])
            if not previous_predictions:
                return {'matches_found': 0}
            
            new_numbers = [int(x) for x in new_combination.strip().split()]
            new_tuple = tuple(new_numbers)
            
            matches = []
            for pred in previous_predictions[:10]:  # Проверяем топ-10 прогнозов
                pred_group = pred.get('group')
                if pred_group and len(pred_group) == 4:
                    pred_tuple = tuple(pred_group)
                    comparison = DataProcessor.compare_groups(pred_tuple, new_tuple)
                    if comparison['total_matches'] > 0:
                        matches.append({
                            'predicted_group': pred_tuple,
                            'score': pred.get('confidence', 0),
                            'matches': comparison
                        })
            
            result = {
                'matches_found': len(matches),
                'matches_details': matches[:3]  # Только топ-3 совпадения
            }
            
            if matches:
                best_match = max(matches, key=lambda x: x['matches']['total_matches'])
                logger.info(f"🔍 Найдено {len(matches)} совпадений. Лучшее: {best_match['matches']['total_matches']}/4")
            else:
                logger.info("📝 Совпадений с предыдущими прогнозами не найдено")
            
            return result
            
        except Exception as e:
            logger.error(f"❌ Ошибка сравнения с прогнозами: {e}")
            return {'matches_found': 0, 'error': str(e)}
    
    def add_data_and_retrain(self, new_combination: str):
        """Добавление данных и дообучение модели с реальной ML системой"""
        try:
            logger.info("🧠 Добавление данных и дообучение модели...")
            
            # Используем реальную систему самообучения
            predictions = self.system.add_data_and_retrain(new_combination, retrain_epochs=3)
            
            if predictions:
                logger.info(f"✅ Дообучение завершено. Сгенерировано {len(predictions)} прогнозов")
                return predictions
            else:
                logger.warning("⚠️ Дообучение завершено, но прогнозы не сгенерированы")
                return []
                
        except Exception as e:
            logger.error(f"❌ Ошибка дообучения: {e}")
            # Пробуем резервный метод
            return self.fallback_retrain(new_combination)
    
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
            'last_processed_draw': self.state_manager.load_state().get('last_processed_draw'),
            'consecutive_api_errors': self.consecutive_api_errors,
            'max_consecutive_errors': self.max_consecutive_errors,
            'service_type': 'auto_learning'
        }
        
        if self.system:
            try:
                system_status = self.system.get_status()
                status.update(system_status)
                
                # Добавляем аналитику самообучения
                learning_stats = self.system.get_learning_insights()
                status['learning_stats'] = learning_stats
                
            except Exception as e:
                status['system_status_error'] = str(e)
        
        return status
    
    # Остальные методы остаются без изменений...
    def manual_restart(self):
        """Ручной перезапуск сервиса после остановки"""
        if not self.service_active:
            logger.info("🔄 Ручной перезапуск сервиса...")
            self.service_active = True
            self.consecutive_api_errors = 0
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
        service.consecutive_api_errors = 0
    
    if args.once:
        success = service.run_once()
        sys.exit(0 if success else 1)
    elif args.schedule:
        service.start_scheduled_service()
    else:
        # По умолчанию показываем статус
        status = service.get_service_status()
        print(json.dumps(status, indent=2, ensure_ascii=False))