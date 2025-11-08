# [file name]: ml/utils/data_utils.py
"""
Утилиты для работы с данными - ДЛЯ СОВМЕСТИМОСТИ
"""

import json
import os
from typing import List, Tuple, Dict
from config.paths import DATA_DIR

def load_dataset() -> List[str]:
    """Загрузка dataset.json"""
    dataset_path = os.path.join(DATA_DIR, "datasets", "dataset.json")
    
    if not os.path.exists(dataset_path):
        return []
    
    try:
        with open(dataset_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        return data if isinstance(data, list) else []
    except:
        return []

def save_dataset(data: List[str]) -> None:
    """Сохранение dataset.json"""
    dataset_path = os.path.join(DATA_DIR, "datasets", "dataset.json")
    os.makedirs(os.path.dirname(dataset_path), exist_ok=True)
    
    try:
        with open(dataset_path, 'w', encoding='utf-8') as f:
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

def load_predictions() -> List[tuple]:
    """Загрузка последних предсказаний"""
    predictions_path = os.path.join(DATA_DIR, "analytics", "predictions_state.json")
    
    if not os.path.exists(predictions_path):
        return []
    
    try:
        with open(predictions_path, 'r', encoding='utf-8') as f:
            state = json.load(f)
        
        predictions = []
        for item in state.get('predictions', []):
            group = tuple(item['group'])
            score = item['score']
            predictions.append((group, score))
        
        return predictions
    except:
        return []

def save_predictions(predictions: List[tuple]) -> None:
    """Сохранение последних предсказаний"""
    predictions_path = os.path.join(DATA_DIR, "analytics", "predictions_state.json")
    os.makedirs(os.path.dirname(predictions_path), exist_ok=True)
    
    try:
        state = {
            'predictions': [
                {'group': list(group), 'score': score} for group, score in predictions
            ]
        }
        with open(predictions_path, 'w', encoding='utf-8') as f:
            json.dump(state, f, ensure_ascii=False, indent=2)
    except Exception as e:
        print(f"❌ Ошибка сохранения предсказаний: {e}")
