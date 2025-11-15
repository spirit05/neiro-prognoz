"""
Расширенный оптимизатор с адаптивными стратегиями
"""
import torch
from typing import Any

from ml.training import AbstractOptimizer
from ml.core.types import TrainingConfig
from ml.core.base_model import AbstractBaseModel


class EnhancedOptimizer(AbstractOptimizer):
    """Расширенный оптимизатор с поддержкой различных стратегий"""
    
    def configure_optimizer(self, model: AbstractBaseModel, config: TrainingConfig) -> Any:
        """Конфигурация оптимизатора с адаптивными параметрами"""
        
        # 🔧 ДОБАВЛЯЕМ ПРОВЕРКУ: Убеждаемся, что модель инициализирована
        if not hasattr(model, 'model') or model.model is None:
            raise ValueError("Модель не инициализирована для конфигурации оптимизатора")
 
        # Разные стратегии оптимизации в зависимости от типа модели
        if hasattr(model, 'model_type'):
            if model.model_type.value == 'classification':
                return torch.optim.AdamW(
                    model.model.parameters(),
                    lr=config.learning_rate,
                    weight_decay=0.01
                )
        
        # Оптимизатор по умолчанию
        return torch.optim.Adam(
            model.model.parameters(),
            lr=config.learning_rate
        )
    
    def get_scheduler(self, optimizer: Any, config: TrainingConfig) -> Any:
        """Получение learning rate scheduler"""
        return torch.optim.lr_scheduler.ReduceLROnPlateau(
            optimizer,
            mode='min',
            factor=0.5,
            patience=5,
            verbose=True
        )
