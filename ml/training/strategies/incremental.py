"""
Стратегия инкрементального обучения - чистая реализация
"""
import torch
from typing import Dict, Any
import time

from ml.training import AbstractTrainingStrategy
from ml.core.types import TrainingConfig, TrainingResult, DataBatch, ModelStatus
from ml.core.base_model import AbstractBaseModel


class IncrementalTrainingStrategy(AbstractTrainingStrategy):
    """Стратегия дообучения модели на новых данных"""
    
    def __init__(self):
        super().__init__("incremental_training")
    
    def train(self, model: AbstractBaseModel, data: DataBatch, config: TrainingConfig) -> TrainingResult:
        """Дообучение модели на новых данных"""
        self._notify_progress("🔄 Начало инкрементального обучения")
        
        training_start = time.time()
        
        try:
            # Используем меньший learning rate для дообучения
            incremental_config = TrainingConfig(
                batch_size=config.batch_size,
                learning_rate=config.learning_rate * 0.5,  # Меньше LR для тонкой настройки
                epochs=min(config.epochs, 10),  # Меньше эпох для дообучения
                early_stopping_patience=config.early_stopping_patience,
                validation_split=config.validation_split
            )
            
            # Для инкрементального обучения можно добавить специальную логику:
            # - Заморозка части слоев
            # - Different learning rates для разных слоев
            # - Регуляризация для сохранения предыдущих знаний
            
            # Временная реализация - используем базовую стратегию с адаптированными параметрами
            from .basic_training import BasicTrainingStrategy
            basic_strategy = BasicTrainingStrategy()
            
            # Передаем callbacks
            for callback in self._callbacks:
                basic_strategy.add_callback(callback)
            
            result = basic_strategy.train(model, data, incremental_config)
            
            self._notify_progress("✅ Инкрементальное обучение завершено")
            return result
            
        except Exception as e:
            self._notify_progress(f"❌ Ошибка инкрементального обучения: {e}")
            raise
    
    def validate(self, model: AbstractBaseModel, data: DataBatch) -> Dict[str, float]:
        """Валидация после дообучения"""
        # Специфичная валидация для инкрементального обучения
        # Можно добавить метрики для оценки "catastrophic forgetting"
        from .basic_training import BasicTrainingStrategy
        basic_strategy = BasicTrainingStrategy()
        return basic_strategy.validate(model, data)
