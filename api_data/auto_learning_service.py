# api_data/auto_learning_service.py
#!/usr/bin/env python3
"""
Автономный сервис для автоматического получения данных и дообучения
С УМНЫМ РАСПИСАНИЕМ И TELEGRAM УВЕДОМЛЕНИЯМИ
"""

import os
import sys
import time
import json
import logging
import fcntl
import subprocess
import requests
from datetime import datetime, timedelta
import schedule

# Добавляем пути для импорта
PROJECT_PATH = '/opt/project'
sys.path.insert(0, PROJECT_PATH)
sys.path.insert(0, os.path.join(PROJECT_PATH, 'model'))
sys.path.insert(0, os.path.dirname(__file__))

# Настройка логирования
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('/opt/project/api_data/auto_learning.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger('AutoLearningService')

# Константы
MAX_API_RETRIES = 3
API_RETRY_DELAY = 30
SERVICE_STATE_FILE = os.path.join(os.path.dirname(__file__), 'service_state.json')
TELEGRAM_CONFIG_FILE = os.path.join(os.path.dirname(__file__), 'telegram_config.json')

class FileLock:
    """Класс для блокировки файлов"""
    def __init__(self, filename):
        self.filename = filename
        self.lockfile = filename + ".lock"
        self.fd = None
    
    def __enter__(self):
        self.fd = open(self.lockfile, 'w')
        try:
            fcntl.flock(self.fd.fileno(), fcntl.LOCK_EX | fcntl.LOCK_NB)
            return self
        except IOError:
            self.fd.close()
            raise RuntimeError(f"Файл {self.filename} заблокирован другим процессом")
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        if self.fd:
            fcntl.flock(self.fd.fileno(), fcntl.LOCK_UN)
            self.fd.close()
            try:
                os.remove(self.lockfile)
            except:
                pass

class TelegramNotifier:
    """Класс для работы с Telegram"""
    
    def __init__(self):
        self.config = self.load_config()
    
    def load_config(self):
        """Загрузка конфигурации Telegram"""
        try:
            if os.path.exists(TELEGRAM_CONFIG_FILE):
                with open(TELEGRAM_CONFIG_FILE, 'r', encoding='utf-8') as f:
                    return json.load(f)
            return {'enabled': False}
        except Exception as e:
            logger.error(f"❌ Ошибка загрузки конфига Telegram: {e}")
            return {'enabled': False}
    
    def send_message(self, message, retry_critical=False):
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
    
    def send_critical_error(self, draw, error_message, stacktrace=None):
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
    
    def send_service_stop(self, draw, reason):
        """Отправка уведомления об остановке сервиса"""
        if not self.config.get('notifications', {}).get('service_stop', False):
            return
        
        message = f"🛑 <b>ОСТАНОВКА СЕРВИСА</b>\n"
        message += f"📦 Тираж: {draw}\n"
        message += f"🕐 Время: {datetime.now().strftime('%H:%M:%S')}\n"
        message += f"📝 Причина: {reason}\n"
        message += f"🔧 Требуется ручной перезапуск"
        
        self.send_message(message, retry_critical=True)
    
    def send_predictions(self, predictions, draw):
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
    
    def process_status_command(self, status_data):
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
    
    def format_status_message(self, status_data):
        """Форматирование сообщения статуса"""
        message = "🤖 <b>СТАТУС АВТОСЕРВИСА</b>\n\n"
        
        # Статус сервиса
        service_status = "✅ Активен" if status_data.get('service_active') else "🛑 Остановлен"
        message += f"{service_status}\n"
        
        # Модель
        model_status = "✅ Обучена" if status_data.get('model_trained') else "⚠️ Не обучена"
        message += f"🎯 Модель: {model_status}\n"
        
        # Данные
        message += f"📊 Групп в датасете: {status_data.get('dataset_size', 0)}\n"
        
        # Последний тираж
        last_draw = status_data.get('last_processed_draw', 'Нет')
        message += f"🕐 Последний тираж: {last_draw}\n"
        
        # Следующий запрос
        next_run = status_data.get('next_scheduled_run')
        if next_run:
            next_time = datetime.fromisoformat(next_run)
            now = datetime.now()
            delta = next_time - now
            minutes = int(delta.total_seconds() // 60)
            message += f"⏰ Следующий запрос: через {minutes} минут\n"
        
        # Веб-версия
        web_status = "✅ Запущена" if status_data.get('web_running') else "❌ Не запущена"
        message += f"🔧 Веб-версия: {web_status}\n\n"
        
        # Прогнозы
        predictions = status_data.get('last_predictions', [])
        if predictions:
            message += "🎯 <b>ПОСЛЕДНИЕ ПРОГНОЗЫ:</b>\n"
            for i, (group, score) in enumerate(predictions[:4], 1):
                confidence = "🟢" if score > 0.02 else "🟡" if score > 0.01 else "🔴"
                message += f"{i}. {group[0]} {group[1]} {group[2]} {group[3]} ({score:.4f}) {confidence}\n"
            message += "\n"
        
        # Аналитика самообучения
        learning_stats = status_data.get('learning_stats', {})
        if learning_stats and 'message' not in learning_stats:
            message += "📈 <b>АНАЛИТИКА САМООБУЧЕНИЯ:</b>\n"
            message += f"🎯 Средняя точность: {learning_stats.get('recent_accuracy_avg', 0)*100:.1f}%\n"
            message += f"📊 Проанализировано: {learning_stats.get('total_predictions_analyzed', 0)} прогнозов\n"
            message += f"🏆 Лучшая точность: {learning_stats.get('best_accuracy', 0)*100:.1f}%\n"
            message += f"📉 Худшая точность: {learning_stats.get('worst_accuracy', 0)*100:.1f}%\n"
            
            recommendations = learning_stats.get('recommendations', [])
            if recommendations:
                message += f"💡 Рекомендации: {recommendations[0]}\n"
        
        return message
    
    def acknowledge_update(self, update_id):
        """Подтверждение обработки команды"""
        try:
            bot_token = self.config.get('bot_token')
            url = f"https://api.telegram.org/bot{bot_token}/getUpdates"
            requests.post(url, json={'offset': update_id + 1}, timeout=5)
        except:
            pass

class AutoLearningService:
    def __init__(self):
        self.system = None
        self.last_processed_draw = None
        self.service_active = True
        self.consecutive_api_errors = 0
        self.max_consecutive_errors = 3
        self.telegram = TelegramNotifier()
        self.next_scheduled_run = None
        self.initialize_system()
        self.load_service_state()
    
    def initialize_system(self):
        """Инициализация AI системы"""
        try:
            from model.simple_system import SimpleNeuralSystem
            
            self.system = SimpleNeuralSystem()
            
            def progress_callback(message):
                logger.info(f"📢 {message}")
            
            self.system.set_progress_callback(progress_callback)
            
            logger.info("✅ AI система инициализирована")
            return True
        except Exception as e:
            logger.error(f"❌ Ошибка инициализации системы: {e}")
            return False
    
    def load_service_state(self):
        """Загрузка состояния сервиса"""
        try:
            if os.path.exists(SERVICE_STATE_FILE):
                with open(SERVICE_STATE_FILE, 'r', encoding='utf-8') as f:
                    state = json.load(f)
                    self.last_processed_draw = state.get('last_processed_draw')
                    self.service_active = state.get('service_active', True)
                    self.consecutive_api_errors = state.get('consecutive_api_errors', 0)
                    
                logger.info(f"📦 Состояние сервиса загружено: активен={self.service_active}")
        except Exception as e:
            logger.warning(f"⚠️ Не удалось загрузить состояние сервиса: {e}")
    
    def save_service_state(self):
        """Сохранение состояния сервиса"""
        try:
            state = {
                'last_processed_draw': self.last_processed_draw,
                'service_active': self.service_active,
                'consecutive_api_errors': self.consecutive_api_errors,
                'last_update': datetime.now().isoformat()
            }
            
            with open(SERVICE_STATE_FILE, 'w', encoding='utf-8') as f:
                json.dump(state, f, ensure_ascii=False, indent=2)
        except Exception as e:
            logger.error(f"❌ Ошибка сохранения состояния сервиса: {e}")
    
    def calculate_next_run_time(self):
        """Расчет времени следующего запуска с учетом временных слотов"""
        now = datetime.now()
        current_minute = now.minute
        
        # Временные слоты API
        api_slots = [14, 29, 44, 59]
        
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
        
        # Корректировка коротких интервалов
        if time_until_next < 4:
            time_until_next += 5  # добавляем 5 минут буфера
        
        self.next_scheduled_run = now + timedelta(minutes=time_until_next)
        return time_until_next
    
    def safe_file_operation(self, operation, filename, *args, **kwargs):
        """Безопасная операция с файлом с блокировкой"""
        for attempt in range(MAX_API_RETRIES):
            try:
                with FileLock(filename):
                    return operation(filename, *args, **kwargs)
            except RuntimeError as e:
                if attempt < MAX_API_RETRIES - 1:
                    logger.warning(f"⚠️ Файл {filename} заблокирован. Попытка {attempt + 1}/{MAX_API_RETRIES}")
                    time.sleep(API_RETRY_DELAY)
                else:
                    logger.error(f"❌ Не удалось получить доступ к файлу {filename}: {e}")
                    raise
    
    def get_current_info(self):
        """Безопасное получение текущей информации из info.json"""
        def read_info(filename):
            if not os.path.exists(filename):
                logger.warning(f"📝 Файл {filename} не найден")
                return {}
            try:
                with open(filename, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except Exception as e:
                logger.error(f"❌ Ошибка чтения {filename}: {e}")
                return {}
        
        info_path = os.path.join(os.path.dirname(__file__), 'info.json')
        return self.safe_file_operation(read_info, info_path)
    
    def update_info_json(self, new_draw, new_combination):
        """Обновление info.json с историей"""
        def update_operation(filename, draw, combination):
            # Загружаем текущие данные
            if os.path.exists(filename):
                with open(filename, 'r', encoding='utf-8') as f:
                    data = json.load(f)
            else:
                data = {
                    "current_draw": draw,
                    "service_status": "active",
                    "history": []
                }
            
            # Проверяем дубликаты
            for entry in data.get('history', []):
                if entry.get('draw') == draw:
                    raise ValueError(f"Дубликат тиража: {draw}")
            
            # Проверяем последовательность
            if data.get('history'):
                last_draw = int(data['history'][-1]['draw'])
                current_draw = int(draw)
                if current_draw != last_draw + 1:
                    raise ValueError(f"Разрыв последовательности: {last_draw} -> {current_draw}")
            
            # Добавляем новую запись
            new_entry = {
                "draw": draw,
                "combination": combination,
                "timestamp": datetime.now().isoformat(),
                "processed": False,
                "service_type": "auto_learning"
            }
            
            data['history'].append(new_entry)
            data['current_draw'] = draw
            
            # Сохраняем
            with open(filename, 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
            
            return data
        
        info_path = os.path.join(os.path.dirname(__file__), 'info.json')
        return self.safe_file_operation(update_operation, info_path, new_draw, new_combination)
    
    def mark_entry_processed(self, draw):
        """Помечаем запись как обработанную"""
        def mark_operation(filename, target_draw):
            if not os.path.exists(filename):
                return False
            
            with open(filename, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            for entry in data.get('history', []):
                if entry.get('draw') == target_draw:
                    entry['processed'] = True
                    entry['processing_time'] = datetime.now().isoformat()
                    break
            
            with open(filename, 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
            
            return True
        
        info_path = os.path.join(os.path.dirname(__file__), 'info.json')
        return self.safe_file_operation(mark_operation, info_path, draw)
    
    def is_web_running(self):
        """Проверка, запущена ли веб-версия"""
        try:
            result = subprocess.run(['pgrep', '-f', 'streamlit'], capture_output=True, text=True)
            return result.returncode == 0
        except:
            return False
    
    def call_api_with_retries(self):
        """Вызов API с повторными попытками и обработкой ошибок"""
        from get_group import get_data_with_curl
        
        for attempt in range(MAX_API_RETRIES):
            try:
                logger.info(f"📡 Попытка {attempt + 1}/{MAX_API_RETRIES}: запрос к API...")
                result = get_data_with_curl()
                
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
                        current_info = self.get_current_info()
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
        """Основной метод обработки новой группы"""
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
            
            # Шаг 2: Читаем обновленный info.json
            current_info = self.get_current_info()
            if not current_info:
                logger.error("❌ Не удалось прочитать info.json")
                return False
            
            new_draw = current_info.get('current_draw')
            history = current_info.get('history', [])
            
            if not new_draw or not history:
                logger.error("❌ В info.json отсутствуют необходимые данные")
                return False
            
            # Находим последнюю необработанную запись
            last_unprocessed = None
            for entry in reversed(history):
                if not entry.get('processed', False):
                    last_unprocessed = entry
                    break
            
            if not last_unprocessed:
                logger.info("📝 Нет необработанных записей")
                return True
            
            new_combination = last_unprocessed.get('combination')
            processing_draw = last_unprocessed.get('draw')
            
            if not new_combination:
                logger.error("❌ Не найдена комбинация для обработки")
                return False
            
            logger.info(f"🎯 Обработка тиража {processing_draw}: {new_combination}")
            
            # Шаг 3: Проверяем валидность группы
            from model.data_loader import validate_group
            if not validate_group(new_combination):
                logger.error(f"❌ Невалидная группа: {new_combination}")
                return False
            
            # Шаг 4: Сравниваем с предыдущими прогнозами
            comparison_result = self.compare_with_predictions(new_combination)
            
            # Шаг 5: Добавляем данные и дообучаем модель
            learning_result = self.add_data_and_retrain(new_combination)
            
            # Шаг 6: Помечаем как обработанную
            self.mark_entry_processed(processing_draw)
            
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
            self.last_processed_draw = processing_draw
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
            current_info = self.get_current_info()
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
            from model.data_loader import load_predictions, compare_groups
            
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
    
    def add_data_and_retrain(self, new_combination: str):
        """Добавление данных и дообучение модели"""
        try:
            logger.info("🧠 Добавление данных и дообучение модели...")
            
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
        def save_operation(filename, data):
            if os.path.exists(filename):
                with open(filename, 'r', encoding='utf-8') as f:
                    all_results = json.load(f)
            else:
                all_results = []
            
            all_results.append(data)
            
            if len(all_results) > 100:
                all_results = all_results[-100:]
            
            with open(filename, 'w', encoding='utf-8') as f:
                json.dump(all_results, f, ensure_ascii=False, indent=2)
        
        result_path = os.path.join(os.path.dirname(__file__), 'learning_results.json')
        self.safe_file_operation(save_operation, result_path, result_data)
        logger.info("💾 Результат обучения сохранен")
    
    def get_service_status(self):
        """Получение статуса сервиса"""
        from model.data_loader import load_predictions
        
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
                    status['last_predictions'] = predictions[:4]
                
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
            logger.warning("⏸️ Сервис остановлен. Используйте --force для принудительного запуска.")
            return False
        
        logger.info("🚀 Запуск однократной обработки...")
        
        # Сразу делаем запрос при запуске
        success = self.process_new_group()
        
        # Рассчитываем следующее время запуска
        if success:
            next_interval = self.calculate_next_run_time()
            logger.info(f"⏰ Следующий запрос через {next_interval:.1f} минут")
        
        return success
    
    def start_scheduled_service(self):
        """Запуск сервиса по расписанию"""
        if not self.service_active:
            logger.error("🚨 Сервис остановлен из-за ошибок API. Запуск по расписанию отменен.")
            logger.info("💡 Используйте: python3 auto_learning_service.py --restart")
            return
        
        logger.info("⏰ Запуск сервиса по расписанию")
        
        # Рассчитываем первый интервал
        first_interval = self.calculate_next_run_time()
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