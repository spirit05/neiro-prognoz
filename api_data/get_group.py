import os
import subprocess
import json
from typing import List, Dict, Any

DATA_DIR = os.path.join(os.path.dirname(__file__))
STATE_PATH = os.path.join(DATA_DIR, 'info.json')

def save_info(data: List[str]) -> None:
    """Сохранение последних предсказаний"""
    os.makedirs(os.path.dirname(STATE_PATH), exist_ok=True)
    state = {
        'draw': data[0],
        'combination': data[1]
    }
    with open(STATE_PATH, 'w', encoding='utf-8') as f:
        json.dump(state, f, ensure_ascii=False, indent=2)

def load_info() -> Dict[str, Any]:
    """Загрузка последних данных"""
    if not os.path.exists(STATE_PATH):
        print(f"Файл {STATE_PATH} не найден")
        return {}
    
    try:
        with open(STATE_PATH, 'r', encoding='utf-8') as f:
            state = json.load(f)
        
        return state
    except Exception as e:
        print(f"Ошибка при загрузке {STATE_PATH}: {e}")
        return {}

def prepare_uri() -> List[str]:
    """Подготовка URI для запроса"""
    data = load_info()
    current_draw_str = data.get('draw', '0')

    try:
        # Преобразуем строку в число, выполняем арифметику, затем обратно в строку
        current_draw = int(current_draw_str)
        next_draw = current_draw + 1
    except (ValueError, TypeError):
        print(f"Ошибка: не могу преобразовать '{current_draw_str}' в число")
        next_draw = 1  # значение по умолчанию

    url = f"https://www.stoloto.ru/p/api/mobile/api/v35/service/games/details/draw-combination?game=dvazhdydva&draw={next_draw}"
    
    return [str(next_draw), url]

def get_data_with_curl():
    """Получение данных через curl"""
    data = prepare_uri()
    if not data:
        print("Не удалось подготовить URI")
        return None
        
    draw, url = data
    
    try:
        result = subprocess.run([
            'curl', 
            '-H', 'User-Agent: Mozilla/5.0', 
            '-H', 'Accept: application/json, text/plain, */*',
            '-H', 'Device-Platform: WEB_MOBILE_LINUX',
            '-H', 'Device-Type: MOBILE', 
            '-H', 'Gosloto-Partner: bXMjXFRXZ3coWXh6R3s1NTdUX3dnWlBMLUxmdg',
            '-H', 'gosloto-token: 76b9725602-dcfb02-4fb151-b0df27-949295930e0c26', 
            '-H', 'referer: https://www.stoloto.ru/dvazhdydva/archive',
            url
        ], capture_output=True, text=True, check=True)
        
        if result.returncode == 0:
            # Обработка результата
            response_data = json.loads(result.stdout)
            
            # Извлекаем комбинацию из structured и преобразуем в строку
            combination_structured = response_data.get('combination', {}).get('structured', [])
            combination_string = " ".join(str(num) for num in combination_structured)
            
            # Сохраняем данные
            save_info([draw, combination_string])
            
            return response_data
        else:
            print(f"Ошибка curl: {result.stderr}")
            return None
            
    except subprocess.CalledProcessError as e:
        print(f"Ошибка выполнения curl: {e}")
        return None
    except json.JSONDecodeError as e:
        print(f"Ошибка парсинга JSON: {e}")
        return None
    except Exception as e:
        print(f"Неожиданная ошибка: {e}")
        return None

# Пример использования
if __name__ == "__main__":
    result = get_data_with_curl()
    if result:
        print("Данные получены успешно")
    else:
        print("Не удалось получить данные")
