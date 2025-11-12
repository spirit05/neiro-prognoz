# [file name]: services/auto_learning/service.py (ПОЛНОСТЬЮ ИСПРАВЛЕННАЯ ВЕРСИЯ)
"""
Автономный сервис для автоматического получения данных и дообучения
С ПРАВИЛЬНОЙ ИНТЕГРАЦИЕЙ ML СИСТЕМЫ И ИСПРАВЛЕННЫМИ ИМПОРТАМИ
"""

import os
import sys
import time
import json
import logging
import schedule
import subprocess
from datetime import datetime, timedelta

# 🔧 ПРАВИЛЬНЫЕ ПУТИ ДЛЯ НОВОЙ АРХИТЕКТУРЫ
PROJECT_ROOT = '/opt/dev'
sys.path.insert(0, PROJECT_ROOT)
sys.path.insert(0, os.path.join(PROJECT_ROOT, 'ml'))
sys.path.insert(0, os.path.join(PROJECT_ROOT, 'config'))
sys.path.insert(0, os.path.join(PROJECT_ROOT, 'services', 'auto_learning'))
sys.path.insert(0, os.path.join(PROJECT_ROOT, 'web', 'components'))

# 🔧 ПРАВИЛЬНЫЕ ИМПОРТЫ ДЛЯ НОВОЙ АРХИТЕКТУРЫ
try:
    from services.auto_learning.api_client import APIClient
    from services.auto_learning.scheduler import SmartScheduler
    from services.auto_learning.file_manager import FileLock, safe_file_operation
    from services.auto_learning.state_manager import StateManager
    from services.auto_learning.notifier import TelegramNotifier
    from config.paths import DATA_DIR, LOGS_DIR
    from config.constants import *
except ImportError as e:
    print(f"❌ Ошибка импорта: {e}")
    print("💡 Проверьте структуру проекта и пути импорта")
    sys.exit(1)

# 🔧 ПРАВИЛЬНАЯ НАСТРОЙКА ЛОГГИРОВАНИЯ
def setup_logging():
    """Настройка логирования для новой архитектуры"""
    log_file = os.path.join(LOGS_DIR, 'auto_learning.log')
    os.makedirs(os.path.dirname(log_file), exist_ok=True)
    
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler(log_file),
            logging.StreamHandler()
        ]
    )
    return logging.getLogger('AutoLearningService')

logger = setup_logging()

class AutoLearningService:
    def __init__(self):
        self.system = None
        self.api_client = APIClient()
        self.scheduler = SmartScheduler()
        self.state_manager = StateManager()
        self.telegram = TelegramNotifier()
        self.service_active = True
        self.consecutive_api_errors = 0
        self.max_consecutive_errors = MAX_CONSECUTIVE_ERRORS
        self.last_processed_draw = None
        self.next_scheduled_run = None
        
        self.initialize_system()
        self.load_service_state()
    
    def initialize_system(self):
        """Инициализация AI системы с правильной ML интеграцией"""
        try:
            # 🔧 ПРАВИЛЬНЫЙ ИМПОРТ ДЛЯ НОВОЙ АРХИТЕКТУРЫ
            from web.components.ml_adapter import MLSystemAdapter
            
            # Инициализируем полную систему через адаптер
            self.system = MLSystemAdapter()
            
            # Настраиваем callback для логирования прогресса
            def progress_callback(message):
                logger.info(f"📢 {message}")
            
            self.system.set_progress_callback(progress_callback)
            
            logger.info("✅ AI система инициализирована через MLSystemAdapter")
            return True
            
        except Exception as e:
            logger.error(f"❌ Ошибка инициализации ML системы: {e}")
            # 🔧 СТРОГОЕ СОБЛЮДЕНИЕ NO-FALLBACK POLICY
            return False
        
    def load_service_state(self):
        """Загрузка состояния сервиса с синхронизацией из info.json"""
        try:
            # Сначала загружаем из service_state.json
            state = self.state_manager.load_state()
            if state:
                self.service_active = state.get('service_active', True)
                self.consecutive_api_errors = state.get('consecutive_api_errors', 0)
                stored_draw = state.get('last_processed_draw')
                
                # 🔧 СИНХРОНИЗАЦИЯ: Получаем актуальный тираж из info.json
                current_info = self.api_client.get_current_info()
                history = current_info.get('history', [])
                
                if history:
                    # Находим последний ОБРАБОТАННЫЙ тираж
                    last_processed = None
                    for entry in reversed(history):
                        if entry.get('processed', False):
                            last_processed = entry.get('draw')
                            break
                    
                    # 🔧 ПРИОРИТЕТ: используем актуальные данные из info.json
                    if last_processed:
                        self.last_processed_draw = last_processed
                        logger.info(f"📊 Синхронизирован last_processed_draw из info.json: {last_processed}")
                        
                        # 🔧 ОБНОВЛЯЕМ service_state.json актуальными данными
                        if stored_draw != last_processed:
                            logger.info(f"🔄 Обновляем service_state.json: {stored_draw} -> {last_processed}")
                            self.save_service_state()
                    elif stored_draw:
                        self.last_processed_draw = stored_draw
                        logger.info(f"📊 Используем last_processed_draw из service_state.json: {stored_draw}")
                    else:
                        self.last_processed_draw = None
                else:
                    self.last_processed_draw = stored_draw
                
                logger.info(f"📦 Состояние сервиса загружено: активен={self.service_active}, ошибок={self.consecutive_api_errors}, тираж={self.last_processed_draw}")
                
        except Exception as e:
            logger.warning(f"⚠️ Не удалось загрузить состояние сервиса: {e}")
            # Резервный вариант
            if state:
                self.last_processed_draw = state.get('last_processed_draw')
    
    def save_service_state(self):
        """Сохранение состояния сервиса"""
        try:
            state = {
                'service_active': self.service_active,
                'consecutive_api_errors': self.consecutive_api_errors,
                'last_processed_draw': self.last_processed_draw,
                'last_update': datetime.now().isoformat()
            }
            self.state_manager.save_state(state)
            
            # 🔧 ДОПОЛНИТЕЛЬНОЕ ЛОГИРОВАНИЕ
            logger.info(f"💾 Состояние сохранено: тираж={self.last_processed_draw}")
            
        except Exception as e:
            logger.error(f"❌ Ошибка сохранения состояния сервиса: {e}")
        
    def calculate_next_run_time(self):
        """Расчет времени следующего запуска с учетом временных слотов"""
        now = datetime.now()
        current_minute = now.minute
        
        # 🔧 ИСПОЛЬЗУЕМ КОНСТАНТЫ ИЗ config.constants
        from config.constants import SCHEDULE_MINUTES, BUFFER_MINUTES
        
        # Временные слоты API из констант
        api_slots = SCHEDULE_MINUTES
        
        # Находим следующий слот
        next_slot = None
        for slot in api_slots:
            if current_minute < slot:
                next_slot = slot
                break
        
        # Если все слоты прошли в этом часе, берем первый слот следующего часа
        if next_slot is None:
            next_time = now.replace(hour=now.hour+1, minute=api_slots[0], second=0, microsecond=0)
        else:
            next_time = now.replace(minute=next_slot, second=0, microsecond=0)
        
        # Расчет интервала до следующего слота
        time_until_next = (next_time - now).total_seconds() / 60  # в минутах
        
        # 🔧 Корректировка коротких интервалов из констант
        if time_until_next < BUFFER_MINUTES:
            time_until_next += BUFFER_MINUTES
        
        self.next_scheduled_run = now + timedelta(minutes=time_until_next)
        return time_until_next
    
    def is_web_running(self):
        """Проверка, запущена ли веб-версия"""
        try:
            result = subprocess.run(['pgrep', '-f', 'streamlit'], capture_output=True, text=True)
            return result.returncode == 0
        except:
            return False
    
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

    def check_draw_synchronization(self):
        """Проверка синхронизации тиражей - ЕДИНСТВЕННЫЙ МЕТОД"""
        try:
            logger.info("🔍 Проверка синхронизации тиражей...")
            
            # Получаем информацию о тиражах из API
            api_info = self.api_client.get_current_draw_info()
            if not api_info:
                logger.error("❌ Не удалось получить информацию о тиражах из API")
                return False
            
            api_current_draw = api_info.get('current_draw')  # Текущий тираж который можно запросить (309381)
            api_next_draw = api_info.get('next_draw')       # Следующий тираж (еще не доступен) (309382)
            
            logger.info(f"📊 API: текущий={api_current_draw}, следующий={api_next_draw}")
            
            # Получаем локальные данные
            local_info = self.api_client.get_current_info()
            history = local_info.get('history', [])
            
            # Находим последний обработанный тираж
            last_processed_draw = None
            for entry in reversed(history):
                if entry.get('processed', False):
                    last_processed_draw = entry.get('draw')
                    break
            
            if not last_processed_draw:
                logger.info("📝 Нет обработанных тиражей в истории")
                last_processed_draw = history[-1].get('draw') if history else None
            
            logger.info(f"📊 Локально: последний обработанный={last_processed_draw}")
            
            # 🔧 ПРАВИЛЬНАЯ ЛОГИКА: ожидаем следующий = последний_обработанный + 1
            expected_next_draw = str(int(last_processed_draw) + 1) if last_processed_draw else api_current_draw
            
            logger.info(f"📊 Ожидаем следующий: {expected_next_draw}")
            
            # 🔧 СРАВНИВАЕМ: ожидаемый следующий должен равняться API текущему
            if expected_next_draw != api_current_draw:
                logger.error(f"🚨 РАСХОЖДЕНИЕ ТИРАЖЕЙ! Ожидался {expected_next_draw}, но API показывает {api_current_draw}")
                logger.error("🔧 Возможные причины: пропущен тираж, ручное изменение данных, ошибка API")
                return False
            
            logger.info("✅ Синхронизация тиражей подтверждена")
            return True
            
        except Exception as e:
            logger.error(f"❌ Ошибка проверки синхронизации: {e}")
            return False

    def process_new_group(self):
        """Основной метод обработки новой группы - ПОЛНАЯ ИНТЕГРАЦИЯ С ML СИСТЕМОЙ"""
        if not self.service_active:
            logger.info("⏸️ Сервис остановлен из-за ошибок API. Требуется ручной перезапуск.")
            return False
        
        logger.info("🔄 Запуск ПОЛНОЙ обработки новой группы...")
        
        try:
            # 🔍 ШАГ 0: ПРОВЕРКА СИНХРОНИЗАЦИИ ПРИ ПЕРВОМ ЗАПУСКЕ
            if self.last_processed_draw is None:
                if not self.check_draw_synchronization():
                    logger.error("🚨 ОШИБКА СИНХРОНИЗАЦИИ ТИРАЖЕЙ! Сервис остановлен.")
                    self.service_active = False
                    self.save_service_state()
                    return False
            
            # 📡 ШАГ 1: Получаем новую группу через API
            result = self.call_api_with_retries()
            
            if not result:
                return False
            
            # 🔎 ШАГ 2: Находим последнюю необработанную запись
            last_unprocessed = self.api_client.get_last_unprocessed_entry()
            if not last_unprocessed:
                logger.info("📝 Нет необработанных записей")
                return True
            
            processing_draw = last_unprocessed.get('draw')
            new_combination = last_unprocessed.get('combination')
            
            logger.info(f"🎯 Обработка тиража {processing_draw}: {new_combination}")
            
            # 🔧 ШАГ 3: Проверяем что тираж следующий по порядку
            if self.last_processed_draw:
                expected_draw = str(int(self.last_processed_draw) + 1)
                if processing_draw != expected_draw:
                    logger.error(f"🚨 НЕОЖИДАННЫЙ ТИРАЖ! Ожидался {expected_draw}, получен {processing_draw}")
                    return False
            
            # ✅ ШАГ 4: Проверяем валидность группы
            from ml.utils.data_utils import validate_group
            if not validate_group(new_combination):
                logger.error(f"❌ Невалидная группа: {new_combination}")
                return False
            
            # 🔄 ШАГ 5: КРИТИЧЕСКИЙ - Интеграция с ML системой
            logger.info("🔗 ИНТЕГРАЦИЯ С ML СИСТЕМОЙ...")
            
            # 🔧 ИСПРАВЛЕНИЕ: Вызываем add_data_and_retrain для полного цикла
            learning_result = self.system.add_data_and_retrain(new_combination, retrain_epochs=RETRAIN_EPOCHS)
            
            if not learning_result:
                logger.error("❌ Ошибка в add_data_and_retrain - данные не обработаны")
                return False
            
            # 📊 ШАГ 6: Сравниваем с предыдущими прогнозами
            comparison_result = self.compare_with_predictions(new_combination)
            
            # 🏷️ ШАГ 7: Помечаем как обработанную
            self.api_client.mark_entry_processed(processing_draw)
            
            # 💾 ШАГ 8: Сохраняем результат обучения
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
            self.last_processed_draw = processing_draw
            self.save_service_state()
          
            # 📨 ШАГ 9: Сохраняем прогнозы и тправляем если включено
            if learning_result:
                from ml.utils.data_utils import save_predictions
                save_predictions(learning_result)
                logger.info(f"💾 Явно сохранено {len(learning_result)} прогнозов в service.py")
                self.telegram.send_predictions(
                    learning_result, 
                    processing_draw, 
                    new_combination,
                    comparison_result
                )
                        
            logger.info(f"✅ ПОЛНАЯ обработка завершена! Новых прогнозов: {len(learning_result)}")
            
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
            from ml.utils.data_utils import load_predictions, compare_groups
            
            previous_predictions = load_predictions()
            if not previous_predictions:
                logger.info("📝 Нет предыдущих прогнозов для сравнения")
                return {'matches_found': 0}
            
            new_numbers = [int(x) for x in new_combination.strip().split()]
            new_tuple = tuple(new_numbers)
            
            matches = []
            for pred_group, score in previous_predictions:
                comparison = compare_groups(pred_group, new_tuple)
                if comparison['total_matches'] > 0:
                    matches.append({
                        'predicted_group': pred_group,
                        'score': score,
                        'matches': comparison
                    })
            
            result = {
                'matches_found': len(matches),
                'matches_details': matches[:3]
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
    
    def save_learning_result(self, result_data):
        """Сохранение результата обучения"""
        try:
            result_path = os.path.join(PROJECT_ROOT, 'data', 'analytics', 'learning_results.json')
            
            def save_operation(filename, data):
                # 🔧 ИСПРАВЛЕНИЕ: Проверяем и корректно обрабатываем структуру файла
                if os.path.exists(filename):
                    with open(filename, 'r', encoding='utf-8') as f:
                        try:
                            file_content = json.load(f)
                            # Если это список - используем как есть, иначе создаем новый
                            if isinstance(file_content, list):
                                all_results = file_content
                            else:
                                all_results = [file_content] if file_content else []
                        except json.JSONDecodeError:
                            all_results = []
                else:
                    all_results = []
                
                # 🔧 Добавляем новые данные
                all_results.append(data)
                
                # Ограничиваем размер истории
                if len(all_results) > 100:
                    all_results = all_results[-100:]
                
                # Сохраняем обратно
                with open(filename, 'w', encoding='utf-8') as f:
                    json.dump(all_results, f, ensure_ascii=False, indent=2)
                
                return True
            
            success = safe_file_operation(save_operation, result_path, result_data)
            if success:
                logger.info("💾 Результат обучения сохранен")
            else:
                logger.error("❌ Не удалось сохранить результат обучения")
                
        except Exception as e:
            logger.error(f"❌ Ошибка сохранения результата обучения: {e}")
    
    def get_service_status(self):
        """Получение статуса сервиса - ПОЛНАЯ СОВМЕСТИМОСТЬ"""
        from ml.utils.data_utils import load_predictions
        
        status = {
            'timestamp': datetime.now().isoformat(),
            'service_active': self.service_active,
            'system_initialized': self.system is not None,
            'last_processed_draw': self.last_processed_draw,
            'model_trained': self.system.is_trained if self.system else False,
            'web_running': self.is_web_running(),
            'consecutive_api_errors': self.consecutive_api_errors,
            'max_consecutive_errors': self.max_consecutive_errors,
            'next_scheduled_run': self.next_scheduled_run.isoformat() if self.next_scheduled_run else None,
            'service_type': 'auto_learning'
        }
        
        if self.system:
            try:
                system_status = self.system.get_status()
                status.update(system_status)
                
                # Добавляем прогнозы
                predictions = load_predictions()
                if predictions:
                    status['last_predictions'] = predictions[:ENSEMBLE_TOP_K]
                
                # Добавляем аналитику самообучения
                learning_stats = self.system.get_learning_insights()
                status['learning_stats'] = learning_stats
                
            except Exception as e:
                status['system_status_error'] = str(e)
        
        return status
    
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
            logger.info("🔄 Ручной star once сервиса...")
            self.service_active = True
            self.consecutive_api_errors = 0
                    
        # Сразу делаем запрос при запуске
        success = self.process_new_group()

        if self.service_active:
            logger.info("🔄 Ручной stop сервиса...")
            self.service_active = False
            
        return success
    
    def start_scheduled_service(self):
        """Запуск сервиса по расписанию с НЕМЕДЛЕННЫМ запросом после проверки"""
        if not self.service_active:
            logger.error("🚨 Сервис остановлен из-за ошибок API. Запуск по расписанию отменен.")
            logger.info("💡 Используйте: python3 service.py --restart")
            return
        
        logger.info("⏰ Запуск сервиса по расписанию")
        
        # 🔧 ШАГ 1: ПРОВЕРКА СИНХРОНИЗАЦИИ
        logger.info("🔍 ВЫПОЛНЕНИЕ ПРОВЕРКИ СИНХРОНИЗАЦИИ ТИРАЖЕЙ...")
        if not self.check_draw_synchronization():
            logger.error("🚨 ОШИБКА СИНХРОНИЗАЦИИ ТИРАЖЕЙ! Сервис остановлен.")
            self.service_active = False
            self.save_service_state()
            
            # Telegram уведомление
            current_info = self.api_client.get_current_info()
            current_draw = current_info.get('current_draw', 'unknown')
            self.telegram.send_service_stop(current_draw, "Расхождение тиражей при запуске")
            return
        
        logger.info("✅ Проверка синхронизации пройдена")
        
        # 🔧 ШАГ 2: НЕМЕДЛЕННЫЙ ЗАПРОС АКТУАЛЬНОГО ТИРАЖА
        logger.info("🚀 НЕМЕДЛЕННЫЙ ЗАПРОС АКТУАЛЬНОГО ТИРАЖА...")
        immediate_success = self.process_new_group()
        
        if not immediate_success:
            logger.error("❌ Немедленный запрос не удался!")
            if not self.service_active:
                logger.error("🚨 Сервис остановлен из-за ошибки при запуске")
                return
        else:
            logger.info("✅ Немедленный запрос выполнен успешно")
        
        # 🔧 ШАГ 3: НАСТРОЙКА РАСПИСАНИЯ (только после немедленного запроса)
        first_interval = self.calculate_next_run_time()
        logger.info(f"⏰ Следующий запрос через {first_interval:.1f} минут")
        
        # Настраиваем расписание
        schedule.every(15).minutes.do(self.safe_scheduled_task)
        
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

