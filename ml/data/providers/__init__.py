# ml/data/providers/__init__.py
# 🔧 ДОБАВЛЯЕМ импорт PredictionsManager

from .dataset_manager import DatasetManager
from .predictions_manager import PredictionsManager  # 🔧 ДОБАВЛЕНО

__all__ = [
    'DatasetManager',
    'PredictionsManager'  # 🔧 ДОБАВЛЕНО
]
