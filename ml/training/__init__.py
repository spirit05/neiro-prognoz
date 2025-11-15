"""
Абстрактные интерфейсы training системы
Чистая архитектура без legacy связей
"""
from abc import ABC, abstractmethod
from typing import Dict, Any, List, Optional
from pathlib import Path
from ml.core.types import TrainingConfig, TrainingResult, DataBatch, ModelStatus
from ml.core.base_model import AbstractBaseModel


class AbstractTrainingStrategy(ABC):
    """Абстрактная стратегия обучения моделей"""
    
    def __init__(self, strategy_id: str):
        self.strategy_id = strategy_id
        self._callbacks: List[callable] = []
    
    @abstractmethod
    def train(self, model: AbstractBaseModel, data: DataBatch, config: TrainingConfig) -> TrainingResult:
        """Обучение модели с указанной конфигурацией"""
        pass
    
    @abstractmethod
    def validate(self, model: AbstractBaseModel, data: DataBatch) -> Dict[str, float]:
        """Валидация модели на данных"""
        pass
    
    def add_callback(self, callback: callable) -> None:
        """Добавление callback для мониторинга прогресса"""
        self._callbacks.append(callback)
    
    def _notify_progress(self, message: str, progress: float = None) -> None:
        """Уведомление о прогрессе через callbacks"""
        for callback in self._callbacks:
            callback(message, progress)


class AbstractOptimizer(ABC):
    """Абстрактный оптимизатор обучения"""
    
    @abstractmethod
    def configure_optimizer(self, model: AbstractBaseModel, config: TrainingConfig) -> Any:
        """Конфигурация оптимизатора для модели"""
        pass
    
    @abstractmethod
    def get_scheduler(self, optimizer: Any, config: TrainingConfig) -> Any:
        """Получение scheduler для оптимизатора"""
        pass
