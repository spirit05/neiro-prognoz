
# [file name]: services/auto_learning/api_client.py
"""
API Client для получения данных с stoloto.ru - ИСПРАВЛЕННЫЕ ПУТИ
"""

import os
import json
import subprocess
import time
from datetime import datetime
from typing import Dict, Any, Optional

# ✅ ПРАВИЛЬНЫЕ ИМПОРТЫ
import sys
sys.path.insert(0, '/opt/dev')
from config.paths import INFO_FILE, DATA_DIR
from config.constants import MAX_API_RETRIES, API_RETRY_DELAY, API_GET_GROUP_URI, API_GET_LAST_DRAW_URI

class APIClient:
    def __init__(self):
        self.info_path = INFO_FILE  # ✅ ПРАВИЛЬНЫЙ ПУТЬ
        self.max_retries = MAX_API_RETRIES
        self.retry_delay = API_RETRY_DELAY
    
    def get_current_info(self) -> Dict[str, Any]:
        """Получение текущей информации из info.json"""
        try:
            if not os.path.exists(self.info_path):
                return {}
            
            with open(self.info_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception as e:
            print(f"❌ Ошибка чтения info.json: {e}")
            return {}

    def get_last_entry(self) -> Optional[Dict[str, Any]]:
        """Получение последней записи из info.json"""
        info = self.get_current_info()
        history = info.get('history', [])
        
        if not history:
            return None
        else:
            return history[-1]

    
    def get_last_unprocessed_entry(self) -> Optional[Dict[str, Any]]:
        """Поиск последней необработанной записи"""
        info = self.get_current_info()
        history = info.get('history', [])
        
        for entry in reversed(history):
            if not entry.get('processed', False):
                return entry
        
        return None
    
    def mark_entry_processed(self, draw: str) -> bool:
        """Пометка записи как обработанной"""
        try:
            if not os.path.exists(self.info_path):
                return False
            
            with open(self.info_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            for entry in data.get('history', []):
                if entry.get('draw') == draw:
                    entry['processed'] = True
                    entry['processing_time'] = datetime.now().isoformat()
                    break
            
            with open(self.info_path, 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
            
            return True
        except Exception as e:
            print(f"❌ Ошибка пометки записи: {e}")
            return False
    
    def get_data_with_retries(self) -> Optional[Dict[str, Any]]:
        """Получение данных с повторными попытками"""
        for attempt in range(self.max_retries):
            try:
                print(f"📡 Попытка {attempt + 1}/{self.max_retries}: запрос к API...")
                result = self._call_api()
                
                if result:
                    return result
                else:
                    print(f"⚠️ Ошибка API (попытка {attempt + 1})")
                    if attempt < self.max_retries - 1:
                        time.sleep(self.retry_delay)
                        
            except Exception as e:
                print(f"❌ Исключение при вызове API (попытка {attempt + 1}): {e}")
                if attempt < self.max_retries - 1:
                    time.sleep(self.retry_delay)
        
        return None
    
    def _call_api(self) -> Optional[Dict[str, Any]]:
        """Вызов API stoloto.ru - ИСПРАВЛЕННАЯ ВЕРСИЯ"""
        try:
            # Подготовка URL
            info = self.get_current_info()
            current_draw_str = info.get('current_draw', '0')
            
            try:
                current_draw = int(current_draw_str)
                next_draw = current_draw + 1
            except (ValueError, TypeError):
                next_draw = 1
            
            url = API_GET_GROUP_URI + str(next_draw)
            
            # Выполнение запроса через curl
            result = subprocess.run([
                'curl', 
                '-s', '--max-time', '30',
                '-H', 'User-Agent: Mozilla/5.0', 
                '-H', 'Accept: application/json, text/plain, */*',
                '-H', 'Device-Platform: WEB_MOBILE_LINUX',
                '-H', 'Device-Type: MOBILE', 
                '-H', 'Gosloto-Partner: bXMjXFRXZ3coWXh6R3s1NTdUX3dnWlBMLUxmdg',
                '-H', 'gosloto-token: 76b9725602-dcfb02-4fb151-b0df27-949295930e0c26', 
                '-H', 'referer: https://www.stoloto.ru/dvazhdydva/archive',
                url
            ], capture_output=True, text=True, check=True, timeout=35)
            
            if result.returncode != 0:
                print(f"❌ Curl ошибка: код {result.returncode}")
                return None
            
            # Парсим JSON
            try:
                response_data = json.loads(result.stdout)
            except json.JSONDecodeError as e:
                print(f"❌ Ошибка парсинга JSON: {e}")
                print(f"📄 Ответ: {result.stdout[:200]}...")
                return None
            
            # КРИТИЧЕСКАЯ ПРОВЕРКА: response_data может быть None
            if not response_data:
                print("❌ response_data is None")
                return None
            
            # КРИТИЧЕСКАЯ ПРОВЕРКА: combination может отсутствовать
            if 'combination' not in response_data:
                print("⚠️ В ответе API нет 'combination'")
                return None
            
            combination = response_data['combination']
            
            # КРИТИЧЕСКАЯ ПРОВЕРКА: structured может отсутствовать или быть None
            if not combination or 'structured' not in combination:
                print("⚠️ В combination нет 'structured'")
                return None
            
            combination_structured = combination['structured']
            
            # КРИТИЧЕСКАЯ ПРОВЕРКА: combination_structured может быть None
            if combination_structured is None:
                print("❌ combination_structured is None")
                return None
            
            # КРИТИЧЕСКАЯ ПРОВЕРКА: combination_structured должен быть списком
            if not isinstance(combination_structured, list):
                print(f"❌ combination_structured не список: {type(combination_structured)}")
                return None
            
            # КРИТИЧЕСКАЯ ПРОВЕРКА: список не должен быть пустым
            if not combination_structured:
                print("❌ combination_structured пустой список")
                return None
            
            # ТОЛЬКО ТЕПЕРЬ безопасно создаем строку
            combination_string = " ".join(str(num) for num in combination_structured)
            self._save_info(str(next_draw), combination_string)
            
            print(f"✅ Получена комбинация для тиража {next_draw}: {combination_string}")
            return response_data
            
        except subprocess.TimeoutExpired:
            print("❌ Таймаут вызова API")
            return None
        except Exception as e:
            print(f"❌ Неожиданная ошибка вызова API: {e}")
            return None
    
    def _save_info(self, draw: str, combination: str) -> None:
        """Сохранение данных в info.json - ИСПРАВЛЕННЫЕ ПУТИ"""
        try:
            # Загружаем текущие данные
            current_data = {}
            if os.path.exists(self.info_path):
                with open(self.info_path, 'r', encoding='utf-8') as f:
                    current_data = json.load(f)
            
            # Инициализируем структуру если нужно
            if 'history' not in current_data:
                current_data['history'] = []
            
            # Проверяем дубликаты
            for entry in current_data['history']:
                if entry.get('draw') == draw:
                    print(f"❌ Дубликат тиража: {draw}")
                    return
            
            # Добавляем новую запись
            new_entry = {
                'draw': draw,
                'combination': combination,
                'timestamp': datetime.now().isoformat(),
                'processed': True,
                'service_type': 'api_request'
            }
            
            current_data['history'].append(new_entry)
            current_data['current_draw'] = draw
            
            # Сохраняем
            with open(self.info_path, 'w', encoding='utf-8') as f:
                json.dump(current_data, f, ensure_ascii=False, indent=2)
            
            print(f"✅ Данные сохранены: тираж {draw}, комбинация {combination}")
            
        except Exception as e:
            print(f"❌ Ошибка сохранения данных: {e}")
           
    def get_current_draw_info(self):
        """Получение информации о текущем и следующем тираже из API"""
        try:
            from config.constants import API_GET_LAST_DRAW_URI, API_TIMEOUT
            import requests
            
            # Получаем информацию о времени до следующего тиража
            response = requests.get(API_GET_LAST_DRAW_URI, timeout=API_TIMEOUT)
            if response.status_code == 200:
                data = response.json()
                
                # 🔧 ИСПРАВЛЕНИЕ: Ищем тираж для игры "dvazhdydva"
                draws = data.get('draws', [])
                dvazhdydva_draw = None
                
                for draw in draws:
                    if draw.get('game') == 'dvazhdydva':
                        dvazhdydva_draw = draw
                        break
                
                if dvazhdydva_draw:
                    future_draw = dvazhdydva_draw.get('drawNumber')  # 309380 (будущий)
                    
                    # 🔧 ИСПРАВЛЕНИЕ: API возвращает БУДУЩИЙ тираж
                    # Текущий = будущий - 1
                    # Следующий = будущий (тот что вернул API)
                    current_draw = str(int(future_draw) - 1) if future_draw else None
                    next_draw = str(future_draw) if future_draw else None
                    
                    return {
                        'current_draw': current_draw,  # 309379
                        'next_draw': next_draw,       # 309380
                        'time_to_next': dvazhdydva_draw.get('remainingSeconds'),
                        'game': 'dvazhdydva',
                        'future_draw': future_draw    # для отладки
                    }
                else:
                    logger.error("❌ Не найден тираж для игры 'dvazhdydva' в ответе API")
                    return None
            else:
                logger.error(f"❌ Ошибка API: {response.status_code}")
                return None
                
        except Exception as e:
            logger.error(f"❌ Ошибка получения информации о тиражах: {e}")
            return None
