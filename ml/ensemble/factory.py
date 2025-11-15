# /opt/model/ml/ensemble/factory.py
"""
Фабрика для создания ансамблевых систем - ЧИСТАЯ АРХИТЕКТУРА
"""

from typing import Dict, Any
import importlib
from pathlib import Path

from .base_ensemble import WeightedEnsemblePredictor
from ml.core.base_model import AbstractBaseModel


class EnsembleFactory:
    """Фабрика для создания ансамблевых систем"""
    
    @staticmethod
    def create_from_config(config: Dict[str, Any]) -> WeightedEnsemblePredictor:
        """Создание ансамбля из конфигурации"""
        ensemble_config = config.get('ensemble', {})
        
        # Создаем основной ансамбль
        ensemble = WeightedEnsemblePredictor(
            model_id=ensemble_config.get('model_id', 'default_ensemble')
        )
        
        # Создаем и добавляем предсказатели
        predictors_config = ensemble_config.get('predictors', {})
        for predictor_id, predictor_config in predictors_config.items():
            predictor = EnsembleFactory._create_predictor(predictor_config)
            weight = ensemble_config.get('combiners', {}).get('weighted', {}).get('params', {}).get('weights', {}).get(predictor_id, 1.0)
            
            ensemble.add_predictor(predictor_id, predictor, weight)
        
        return ensemble
    
    @staticmethod
    def _create_predictor(config: Dict[str, Any]) -> AbstractBaseModel:
        """Создание отдельного предсказателя"""
        class_path = config.get('class', '')
        params = config.get('params', {})
        
        if not class_path:
            raise ValueError("Не указан class для предсказателя")
        
        # Динамическая загрузка класса
        module_name, class_name = class_path.rsplit('.', 1)
        module = importlib.import_module(module_name)
        predictor_class = getattr(module, class_name)
        
        # Создание экземпляра
        return predictor_class(**params)
