"""
Оркестратор ML пайплайнов
"""
from typing import Dict, List, Optional, Any
from pathlib import Path
import logging
from datetime import datetime
import pandas as pd

from .base_model import AbstractBaseModel
from .types import (
    ModelType, ModelStatus, TrainingConfig, 
    DataBatch, PredictionRequest, PredictionResponse,
    TrainingResult
)


class MLOrchestrator:
    """
    Оркестратор для управления ML моделями и пайплайнами
    """
    
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.logger = logging.getLogger(__name__)
        
        # Реестр моделей
        self._models: Dict[str, AbstractBaseModel] = {}
        self._model_registry: Dict[str, Dict[str, Any]] = {}
        
        # Статистика
        self._training_history: List[Dict[str, Any]] = []
        self._prediction_stats: Dict[str, int] = {}

    def register_model(self, model: AbstractBaseModel) -> None:
        """
        Регистрация модели в оркестраторе
        
        Args:
            model: Модель для регистрации
        """
        model_id = model.model_id
        
        if model_id in self._models:
            self.logger.warning(f"Model '{model_id}' already registered, overwriting")
            
        self._models[model_id] = model
        self._model_registry[model_id] = {
            'registered_at': datetime.now(),
            'model_type': model.model_type,
            'status': model.status
        }
        
        self.logger.info(f"Model '{model_id}' registered successfully")

    def train_model(
        self, 
        model_id: str, 
        data: DataBatch, 
        config: TrainingConfig
    ) -> TrainingResult:
        """
        Обучение зарегистрированной модели
        
        Args:
            model_id: ID модели
            data: Данные для обучения
            config: Конфигурация обучения
            
        Returns:
            TrainingResult: Результаты обучения
        """
        if model_id not in self._models:
            raise ValueError(f"Model '{model_id}' not found in registry")
            
        model = self._models[model_id]
        self.logger.info(f"Starting training for model '{model_id}'")
        
        try:
            # Валидация данных
            if not model.validate_features(data.data):
                raise ValueError("Feature validation failed")
                
            # Обучение
            result = model.train(data, config)
            
            # Обновление регистра
            self._model_registry[model_id].update({
                'status': result.status,
                'last_trained': datetime.now(),
                'training_metrics': result.metrics
            })
            
            # Сохранение истории
            self._training_history.append({
                'model_id': model_id,
                'timestamp': datetime.now(),
                'result': result.model_dump(),
                'config': config.model_dump()
            })
            
            self.logger.info(f"Training completed for model '{model_id}'")
            return result
            
        except Exception as e:
            self.logger.error(f"Training failed for model '{model_id}': {e}")
            self._model_registry[model_id]['status'] = ModelStatus.FAILED
            raise

    def predict(
        self, 
        request: PredictionRequest
    ) -> PredictionResponse:
        """
        Выполнение предсказания
        
        Args:
            request: Запрос на предсказание
            
        Returns:
            PredictionResponse: Результаты предсказания
        """
        model_id = request.model_id
        
        if model_id not in self._models:
            raise ValueError(f"Model '{model_id}' not found in registry")
            
        model = self._models[model_id]
        
        if not model.is_trained:
            raise ValueError(f"Model '{model_id}' is not trained")
            
        # Создание DataBatch
        data_batch = DataBatch(
            data=request.data if isinstance(request.data, pd.DataFrame) 
                  else pd.DataFrame(request.data),
            batch_id=f"pred_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
            data_type='prediction'
        )
        
        self.logger.info(f"Starting prediction for model '{model_id}'")
        
        try:
            response = model.predict(data_batch)
            
            # Обновление статистики
            self._prediction_stats[model_id] = self._prediction_stats.get(model_id, 0) + 1
            
            return response
            
        except Exception as e:
            self.logger.error(f"Prediction failed for model '{model_id}': {e}")
            raise

    def get_model_info(self, model_id: str) -> Optional[Dict[str, Any]]:
        """Получение информации о модели"""
        if model_id not in self._model_registry:
            return None
            
        model = self._models.get(model_id)
        info = self._model_registry[model_id].copy()
        info['model_id'] = model_id  # Добавляем model_id
        
        if model:
            info.update({
                'metadata': model.metadata.model_dump(),
                'is_trained': model.is_trained,
                'feature_specs': [spec.model_dump() for spec in getattr(model, '_feature_specs', [])]
            })
            
        return info

    def list_models(self) -> List[Dict[str, Any]]:
        """Список всех зарегистрированных моделей"""
        return [
            {
                'model_id': model_id,
                'model_type': info['model_type'].value,
                'status': info['status'].value,
                'registered_at': info['registered_at'],
                'is_trained': self._models[model_id].is_trained if model_id in self._models else False
            }
            for model_id, info in self._model_registry.items()
        ]

    def save_model(self, model_id: str, path: Path) -> None:
        """Сохранение модели"""
        if model_id not in self._models:
            raise ValueError(f"Model '{model_id}' not found")
            
        self._models[model_id].save(path)
        self.logger.info(f"Model '{model_id}' saved to {path}")

    def load_model(self, model_id: str, path: Path, model_class: type) -> None:
        """Загрузка модели"""
        model = model_class(model_id=model_id, model_type=ModelType.REGRESSION)
        model.load(path)
        self.register_model(model)
        self.logger.info(f"Model '{model_id}' loaded from {path}")

    def train_model_with_strategy(
        self, 
        model_id: str,
        strategy_id: str, 
        data: DataBatch, 
        config: TrainingConfig
    ) -> TrainingResult:
        """Обучение модели с указанной стратегией"""
        if model_id not in self._models:
            raise ValueError(f"Model '{model_id}' not found in registry")
        
        # Динамическая загрузка стратегии
        if strategy_id == "basic":
            from ml.training.strategies import BasicTrainingStrategy
            strategy = BasicTrainingStrategy()
        elif strategy_id == "incremental":
            from ml.training.strategies import IncrementalTrainingStrategy
            strategy = IncrementalTrainingStrategy()
        else:
            raise ValueError(f"Unknown strategy: {strategy_id}")
        
        # Добавляем callbacks оркестратора
        def orchestrator_callback(message, progress=None):
            self.logger.info(f"Training progress: {message}")
        
        strategy.add_callback(orchestrator_callback)
        
        # Запуск обучения
        model = self._models[model_id]
        result = strategy.train(model, data, config)
        
        # Обновляем статус модели в регистре
        self._model_registry[model_id]['status'] = result.status
        self._model_registry[model_id]['last_trained'] = datetime.now()
        
        return result

