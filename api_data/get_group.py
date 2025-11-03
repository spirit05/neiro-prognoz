# api_data/get_group.py  
#!/usr/bin/env python3
"""
Получение данных через API с обновленной логикой info.json
"""

import os
import subprocess
import json
import time
from typing import List, Dict, Any
from datetime import datetime

DATA_DIR = os.path.join(os.path.dirname(__file__))
STATE_PATH = os.path.join(DATA_DIR, 'info.json')

def save_info(draw: str, combination: str) -> None:
    """Сохранение данных в info.json с историей"""
    os.makedirs(os.path.dirname(STATE_PATH), exist_ok=True)
    
    # Загружаем текущие данные
    current_data = {}
    if os.path.exists(STATE_PATH):
        try:
            with open(STATE_PATH, 'r', encoding='utf-8') as f:
                current_data = json.load(f)
        except:
            current_data = {}
    
    # Инициализируем структуру если нужно
    if 'history' not in current_data:
        current_data['history'] = []
    
    if 'current_draw' not in current_data:
        current_data['current_draw'] = draw
    
    if 'service_status' not in current_data:
        current_data['service_status'] = 'active'
    
    # Проверяем дубликаты
    for entry in current_data['history']:
        if entry.get('draw') == draw:
            print(f"❌ Дубликат тиража: {draw}")
            return
    
    # Проверяем последовательность
    if current_data['history']:
        last_draw = int(current_data['history'][-1]['draw'])
        current_draw = int(draw)
        if current_draw != last_draw + 1:
            print(f"❌ Разрыв последовательности: {last_draw} -> {current_draw}")
            return
    
    # Добавляем новую запись
    new_entry = {
        'draw': draw,
        'combination': combination,
        'timestamp': datetime.now().isoformat(),
        'processed': False,
        'service_type': 'api_request'
    }
    
    current_data['history'].append(new_entry)
    current_data['current_draw'] = draw
    
    # Сохраняем
    with open(STATE_PATH, 'w', encoding='utf-8') as f:
        json.dump(current_data, f, ensure_ascii=False, indent=2)
    
    print(f"✅ Данные сохранены: тираж {draw}, комбинация {combination}")

def load_info() -> Dict[str, Any]:
    """Загрузка данных из info.json"""
    if not os.path.exists(STATE_PATH):
        print(f"📝 Файл {STATE_PATH} не найден")
        return {}
    
    try:
        with open(STATE_PATH, 'r', encoding='utf-8') as f:
            state = json.load(f)
        
        return state
    except Exception as e:
        print(f"❌ Ошибка при загрузке {STATE_PATH}: {e}")
        return {}

def prepare_uri() -> List[str]:
    """Подготовка URI для запроса"""
    data = load_info()
    current_draw_str = data.get('current_draw', '0')

    try:
        # Преобразуем строку в число, выполняем арифметику, затем обратно в строку
        current_draw = int(current_draw_str)
        next_draw = current_draw + 1
    except (ValueError, TypeError):
        print(f"❌ Ошибка: не могу преобразовать '{current_draw_str}' в число")
        next_draw = 1  # значение по умолчанию

    url = f"https://www.stoloto.ru/p/api/mobile/api/v35/service/games/details/draw-combination?game=dvazhdydva&draw={next_draw}"
    
    return [str(next_draw), url]

def get_data_with_curl():
    """Получение данных через curl с улучшенной обработкой ошибок"""
    data = prepare_uri()
    if not data:
        print("❌ Не удалось подготовить URI")
        return None
        
    draw, url = data
    
    for attempt in range(3):  # 3 попытки
        try:
            print(f"📡 Попытка {attempt + 1}/3: запрос данных для тиража {draw}...")
            
            result = subprocess.run([
                'curl', 
                '-s', '--max-time', '30',  # Таймаут 30 секунд
                '-H', 'User-Agent: Mozilla/5.0', 
                '-H', 'Accept: application/json, text/plain, */*',
                '-H', 'Device-Platform: WEB_MOBILE_LINUX',
                '-H', 'Device-Type: MOBILE', 
                '-H', 'Gosloto-Partner: bXMjXFRXZ3coWXh6R3s1NTdUX3dnWlBMLUxmdg',
                '-H', 'gosloto-token: 76b9725602-dcfb02-4fb151-b0df27-949295930e0c26', 
                '-H', 'referer: https://www.stoloto.ru/dvazhdydva/archive',
                url
            ], capture_output=True, text=True, check=True, timeout=35)
            
            if result.returncode == 0:
                # Обработка результата
                response_data = json.loads(result.stdout)
                
                # Проверяем наличие комбинации
                if 'combination' not in response_data or 'structured' not in response_data['combination']:
                    print("⚠️ В ответе API нет данных о комбинации")
                    if attempt < 2:
                        time.sleep(10)
                        continue
                    return None
                
                # Извлекаем комбинацию из structured и преобразуем в строку
                combination_structured = response_data['combination']['structured']
                combination_string = " ".join(str(num) for num in combination_structured)
                
                # Сохраняем данные
                save_info(draw, combination_string)
                
                print(f"✅ Получена комбинация для тиража {draw}: {combination_string}")
                return response_data
            else:
                print(f"⚠️ Ошибка curl: {result.stderr}")
                if attempt < 2:
                    time.sleep(10)
                    
        except subprocess.TimeoutExpired:
            print(f"⏰ Таймаут попытки {attempt + 1}")
            if attempt < 2:
                time.sleep(10)
                
        except subprocess.CalledProcessError as e:
            print(f"⚠️ Ошибка выполнения curl: {e}")
            if attempt < 2:
                time.sleep(10)
                
        except json.JSONDecodeError as e:
            print(f"⚠️ Ошибка парсинга JSON: {e}")
            if attempt < 2:
                time.sleep(10)
                
        except Exception as e:
            print(f"⚠️ Неожиданная ошибка: {e}")
            if attempt < 2:
                time.sleep(10)
    
    print("❌ Все попытки получения данных провалились")
    return None

# Пример использования
if __name__ == "__main__":
    result = get_data_with_curl()
    if result:
        print("✅ Данные получены успешно")
    else:
        print("❌ Не удалось получить данные")