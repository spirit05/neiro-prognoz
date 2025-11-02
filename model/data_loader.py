# [file name]: model/data_loader.py
"""
Загрузка и работа с данными
"""

import json
import os
import sys
from typing import List, Tuple, Dict

# Добавляем родительскую директорию в путь для импортов
current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(current_dir)
if parent_dir not in sys.path:
    sys.path.insert(0, parent_dir)

DATA_DIR = os.path.join(parent_dir, 'data')
DATASET_PATH = os.path.join(DATA_DIR, 'dataset.json')
STATE_PATH = os.path.join(DATA_DIR, 'predictions_state.json')

def ensure_data_dir():
    """Создание директории данных если не существует"""
    os.makedirs(DATA_DIR, exist_ok=True)

def load_dataset() -> List[str]:
    """Загрузка dataset.json"""
    ensure_data_dir()
    
    if not os.path.exists(DATASET_PATH):
        print("❌ Файл dataset.json не найден, создаем новый")
        return []
    
    try:
        with open(DATASET_PATH, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        if not isinstance(data, list):
            print("❌ Неверный формат dataset.json")
            return []
        
        return data
        
    except Exception as e:
        print(f"❌ Ошибка загрузки dataset.json: {e}")
        return []

def save_dataset(data: List[str]) -> None:
    """Сохранение dataset.json"""
    ensure_data_dir()
    try:
        with open(DATASET_PATH, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
    except Exception as e:
        print(f"❌ Ошибка сохранения dataset.json: {e}")

def validate_group(group_str: str) -> bool:
    """Валидация группы чисел"""
    try:
        numbers = [int(x) for x in group_str.strip().split()]
        if len(numbers) != 4:
            return False
        if not all(1 <= x <= 26 for x in numbers):
            return False
        if numbers[0] == numbers[1] or numbers[2] == numbers[3]:
            return False
        return True
    except:
        return False

def compare_groups(pred_group: Tuple[int, int, int, int], actual_group: Tuple[int, int, int, int]) -> Dict[str, int]:
    """
    Сравнение двух групп с парным учетом
    """
    pred_pair1 = set([pred_group[0], pred_group[1]])
    pred_pair2 = set([pred_group[2], pred_group[3]])
    actual_pair1 = set([actual_group[0], actual_group[1]])
    actual_pair2 = set([actual_group[2], actual_group[3]])
    
    # Совпадения в парах
    pair1_matches = len(pred_pair1.intersection(actual_pair1))
    pair2_matches = len(pred_pair2.intersection(actual_pair2))
    
    # Точные совпадения по позициям
    exact_matches = sum(1 for i in range(4) if pred_group[i] == actual_group[i])
    
    return {
        'total_matches': pair1_matches + pair2_matches,
        'pair1_matches': pair1_matches,
        'pair2_matches': pair2_matches,
        'exact_matches': exact_matches
    }

def save_predictions(predictions: List[tuple]) -> None:
    """Сохранение последних предсказаний"""
    ensure_data_dir()
    try:
        state = {
            'predictions': [
                {'group': list(group), 'score': score} for group, score in predictions
            ]
        }
        with open(STATE_PATH, 'w', encoding='utf-8') as f:
            json.dump(state, f, ensure_ascii=False, indent=2)
    except Exception as e:
        print(f"❌ Ошибка сохранения предсказаний: {e}")

def load_predictions() -> List[tuple]:
    """Загрузка последних предсказаний"""
    ensure_data_dir()
    
    if not os.path.exists(STATE_PATH):
        return []
    
    try:
        with open(STATE_PATH, 'r', encoding='utf-8') as f:
            state = json.load(f)
        
        predictions = []
        for item in state.get('predictions', []):
            group = tuple(item['group'])
            score = item['score']
            predictions.append((group, score))
        
        return predictions
    except:
        return []