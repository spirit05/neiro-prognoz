# [file name]:  ml/utils/data_utils.py
"""
Утилиты для работы с данными - МОДУЛЬНАЯ АРХИТЕКТУРА
"""

import json
import os
from typing import List, Tuple, Dict
from config import paths, security, logging_config

logger = logging_config.get_ml_system_logger()

def load_dataset() -> List[str]:
    """Загрузка dataset.json"""
    return security.SafeFileOperations.read_json_safe(paths.DATASET_FILE, default=[])

def save_dataset(data: List[str]) -> None:
    """Сохранение dataset.json"""
    security.SafeFileOperations.write_json_safe(paths.DATASET_FILE, data)

def validate_group(group_str: str) -> bool:
    """Валидация группы чисел"""
    from config.security import DataValidator
    return DataValidator.validate_group(group_str)

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
    state = {
        'predictions': [
            {'group': list(group), 'score': score} for group, score in predictions
        ]
    }
    security.SafeFileOperations.write_json_safe(paths.PREDICTIONS_STATE_FILE, state)

def load_predictions() -> List[tuple]:
    """Загрузка последних предсказаний"""
    state = security.SafeFileOperations.read_json_safe(paths.PREDICTIONS_STATE_FILE, default={'predictions': []})
    
    predictions = []
    for item in state.get('predictions', []):
        group = tuple(item['group'])
        score = item['score']
        predictions.append((group, score))
    
    return predictions