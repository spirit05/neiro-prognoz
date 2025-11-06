# ml/data/data_loader.py
"""
Загрузка и работа с данными
"""

import json
import os
from typing import List, Tuple, Dict
from config.paths import DATASET, PREDICTIONS
from config.logging_config import setup_logging  # ← ИСПРАВЛЕНО ИМЯ

logger = setup_logging('DataLoader')

def load_dataset() -> List[str]:
    """Загрузка dataset.json"""
    if not os.path.exists(DATASET):
        logger.info("📝 Файл dataset.json не найден, создаем новый")
        return []
    
    try:
        with open(DATASET, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        if not isinstance(data, list):
            logger.error("❌ Неверный формат dataset.json")
            return []
        
        return data
        
    except Exception as e:
        logger.error(f"❌ Ошибка загрузки dataset.json: {e}")
        return []

def save_dataset(data: List[str]) -> None:
    """Сохранение dataset.json"""
    try:
        os.makedirs(os.path.dirname(DATASET), exist_ok=True)
        with open(DATASET, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        logger.info(f"💾 dataset.json сохранен ({len(data)} групп)")
    except Exception as e:
        logger.error(f"❌ Ошибка сохранения dataset.json: {e}")

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
    try:
        os.makedirs(os.path.dirname(PREDICTIONS), exist_ok=True)
        state = {
            'predictions': [
                {'group': list(group), 'score': score} for group, score in predictions
            ]
        }
        with open(PREDICTIONS, 'w', encoding='utf-8') as f:
            json.dump(state, f, ensure_ascii=False, indent=2)
        logger.info(f"💾 Прогнозы сохранены ({len(predictions)} шт)")
    except Exception as e:
        logger.error(f"❌ Ошибка сохранения предсказаний: {e}")

def load_predictions() -> List[tuple]:
    """Загрузка последних предсказаний"""
    if not os.path.exists(PREDICTIONS):
        return []
    
    try:
        with open(PREDICTIONS, 'r', encoding='utf-8') as f:
            state = json.load(f)
        
        predictions = []
        for item in state.get('predictions', []):
            group = tuple(item['group'])
            score = item['score']
            predictions.append((group, score))
        
        return predictions
    except:
        return []