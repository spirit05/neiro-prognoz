# [file name]: ml/features/base.py
"""
Базовые абстракции для feature engineers
"""

from abc import ABC, abstractmethod
from typing import List
import numpy as np

class AbstractFeatureEngineer(ABC):
    """Абстрактный базовый класс для всех feature engineers"""
    
    def __init__(self, history_size: int = 20):
        self.history_size = history_size
        self.is_fitted = False
    
    @abstractmethod
    def extract_features(self, number_history: List[int]) -> np.ndarray:
        """Извлечение features из истории чисел"""
        pass
    
    @abstractmethod
    def get_feature_names(self) -> List[str]:
        """Получение имен features"""
        pass
    
    def fit(self, data: List[int]) -> None:
        """Обучение feature engineer (если требуется)"""
        self.is_fitted = True
