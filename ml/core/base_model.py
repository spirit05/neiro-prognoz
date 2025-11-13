"""
Абстрактные базовые классы для ML моделей
"""
from abc import ABC, abstractmethod
from typing import Dict, List, Optional, Union, Any
import pandas as pd
import numpy as np
import logging
from pathlib import Path

from .types import (
    ModelType, ModelStatus, TrainingConfig, 
    ModelMetadata, TrainingResult, PredictionResponse,
    DataBatch, FeatureSpec
)


class AbstractBaseModel(ABC):
    """
    Абстрактный базовый класс для всех ML моделей
    """
    
    def __init__(self, model_id: str, model_type: ModelType):
        self.model_id = model_id
        self.model_type = model_type
        self.status = ModelStatus.READY
        self.metadata = ModelMetadata(
            model_id=model_id,
            model_type=model_type
        )
        self.logger = logging.getLogger(f"{__name__}.{model_id}")
        
        # Внутреннее состояние
        self._is_trained = False
        self._feature_specs: List[FeatureSpec] = []

    @abstractmethod
    def train(self, data: DataBatch, config: TrainingConfig) -> TrainingResult:
        """
        Обучение модели
        
        Args:
            data: Пакет данных для обучения
            config: Конфигурация обучения
            
        Returns:
            TrainingResult: Результаты обучения
        """
        pass

    @abstractmethod
    def predict(self, data: DataBatch) -> PredictionResponse:
        """
        Предсказание на новых данных
        
        Args:
            data: Пакет данных для предсказания
            
        Returns:
            PredictionResponse: Результаты предсказания
        """
        pass

    @abstractmethod
    def save(self, path: Path) -> None:
        """
        Сохранение модели
        
        Args:
            path: Путь для сохранения
        """
        pass

    @abstractmethod
    def load(self, path: Path) -> None:
        """
        Загрузка модели
        
        Args:
            path: Путь к сохраненной модели
        """
        pass

    def validate_features(self, data: pd.DataFrame) -> bool:
        """
        Валидация входных фич
        
        Args:
            data: Данные для валидации
            
        Returns:
            bool: True если валидация пройдена
        """
        if not self._feature_specs:
            self.logger.warning("No feature specs defined, skipping validation")
            return True
            
        for spec in self._feature_specs:
            if spec.required and spec.name not in data.columns:
                self.logger.error(f"Required feature '{spec.name}' not found")
                return False
                
            if spec.name in data.columns:
                # Проверка типов и значений
                if not self._validate_feature_values(data[spec.name], spec):
                    return False
                    
        return True

    def _validate_feature_values(self, series: pd.Series, spec: FeatureSpec) -> bool:
        """Валидация значений фичи"""
        try:
            # Проверка на NaN для обязательных фич
            if spec.required and series.isna().any():
                self.logger.error(f"Feature '{spec.name}' contains NaN values")
                return False
                
            # Проверка диапазона значений
            if spec.min_value is not None and series.min() < spec.min_value:
                self.logger.error(f"Feature '{spec.name}' values below minimum: {spec.min_value}")
                return False
                
            if spec.max_value is not None and series.max() > spec.max_value:
                self.logger.error(f"Feature '{spec.name}' values above maximum: {spec.max_value}")
                return False
                
            # Проверка категориальных значений
            if spec.allowed_categories:
                invalid_categories = set(series.unique()) - set(spec.allowed_categories)
                if invalid_categories:
                    self.logger.error(f"Feature '{spec.name}' has invalid categories: {invalid_categories}")
                    return False
                    
        except Exception as e:
            self.logger.error(f"Error validating feature '{spec.name}': {e}")
            return False
            
        return True

    def get_feature_importance(self) -> Optional[Dict[str, float]]:
        """
        Получение важности фич
        
        Returns:
            Dict с важностями фич или None если не поддерживается
        """
        self.logger.info("Feature importance not implemented for this model")
        return None

    def update_metadata(self, **kwargs) -> None:
        """Обновление метаданных модели"""
        update_data = {**self.metadata.model_dump(), **kwargs, 'updated_at': self.metadata.updated_at}
        self.metadata = ModelMetadata(**update_data)

    @property
    def is_trained(self) -> bool:
        """Проверка обученности модели"""
        return self._is_trained


class AbstractDataProcessor(ABC):
    """
    Абстрактный класс для обработки данных
    """
    
    @abstractmethod
    def fit_transform(self, data: DataBatch) -> DataBatch:
        """Обучение и преобразование данных"""
        pass

    @abstractmethod
    def transform(self, data: DataBatch) -> DataBatch:
        """Преобразование данных (без обучения)"""
        pass

    @abstractmethod
    def save(self, path: Path) -> None:
        """Сохранение процессора"""
        pass

    @abstractmethod
    def load(self, path: Path) -> None:
        """Загрузка процессора"""
        pass
