# [file name]: ml/utils/data_utils.py
"""
Утилиты для работы с данными - ПЕРЕМЕЩЕНЫ ИЗ СТАРОЙ СТРУКТУРЫ
"""

import json
import os
from typing import List, Tuple, Optional
from pathlib import Path

# 🔧 КОММЕНТАРИЙ: Основные утилиты данных теперь находятся в:
# - ml/data/providers/dataset_manager.py
# - ml/data/quality/validators.py
# - ml/data/processors/data_processor.py

def load_dataset() -> List[str]:
    """Загрузка dataset.json - ДУБЛИРУЕТ ФУНКЦИОНАЛ ДЛЯ ОБРАТНОЙ СОВМЕСТИМОСТИ"""
    try:
        from ml.data.providers.dataset_manager import DatasetManager
        manager = DatasetManager()
        return manager.load_dataset()
    except ImportError:
        # Резервная реализация для обратной совместимости
        dataset_path = Path("data/datasets/dataset.json")
        if dataset_path.exists():
            with open(dataset_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        return []

def save_dataset(data: List[str]) -> bool:
    """Сохранение dataset.json - ДУБЛИРУЕТ ФУНКЦИОНАЛ ДЛЯ ОБРАТНОЙ СОВМЕСТИМОСТИ"""
    try:
        from ml.data.providers.dataset_manager import DatasetManager
        manager = DatasetManager()
        return manager.save_dataset(data)
    except ImportError:
        # Резервная реализация для обратной совместимости
        dataset_path = Path("data/datasets/dataset.json")
        dataset_path.parent.mkdir(parents=True, exist_ok=True)
        try:
            with open(dataset_path, 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
            return True
        except Exception:
            return False

def validate_group(group_str: str) -> bool:
    """Валидация группы - ДУБЛИРУЕТ ФУНКЦИОНАЛ ДЛЯ ОБРАТНОЙ СОВМЕСТИМОСТИ"""
    try:
        from ml.data.quality.validators import DataValidator
        validator = DataValidator()
        return validator.validate_group(group_str)
    except ImportError:
        # Резервная реализация для обратной совместимости
        try:
            numbers = [int(x) for x in group_str.strip().split()]
            return len(numbers) == 4 and all(1 <= x <= 26 for x in numbers)
        except:
            return False

# 🔧 ДОБАВЛЕНО: Функции для работы с прогнозами (если используются в тестах)
def load_predictions():
    """Загрузка прогнозов - ДУБЛИРУЕТ ФУНКЦИОНАЛ ДЛЯ ОБРАТНОЙ СОВМЕСТИМОСТИ"""
    predictions_path = Path("data/predictions.json")
    if predictions_path.exists():
        with open(predictions_path, 'r', encoding='utf-8') as f:
            return json.load(f)
    return []

def save_predictions(predictions):
    """Сохранение прогнозов - ДУБЛИРУЕТ ФУНКЦИОНАЛ ДЛЯ ОБРАТНОЙ СОВМЕСТИМОСТИ"""
    predictions_path = Path("data/predictions.json")
    predictions_path.parent.mkdir(parents=True, exist_ok=True)
    try:
        with open(predictions_path, 'w', encoding='utf-8') as f:
            json.dump(predictions, f, ensure_ascii=False, indent=2)
        return True
    except Exception:
        return False

__all__ = [
    'load_dataset',
    'save_dataset', 
    'validate_group',
    'load_predictions',
    'save_predictions'
]
