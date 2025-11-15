"""
Тесты для ЭТАПА 4 - Training система
"""
import pytest
import torch
import numpy as np
from pathlib import Path

from ml.training import AbstractTrainingStrategy
from ml.training.strategies import BasicTrainingStrategy, IncrementalTrainingStrategy
from ml.training.optimizers import EnhancedOptimizer
from ml.core.types import TrainingConfig, DataBatch, DataType
from ml.models.base.enhanced_predictor import EnhancedPredictor
import pandas as pd


class TestTrainingSystem:
    """Тесты training системы"""
    
    def test_abstract_interfaces(self):
        """Тестирование абстрактных интерфейсов"""
        assert hasattr(AbstractTrainingStrategy, 'train')
        assert hasattr(AbstractTrainingStrategy, 'validate')
        
    def test_basic_training_strategy_initialization(self):
        """Тест инициализации базовой стратегии"""
        strategy = BasicTrainingStrategy()
        assert strategy.strategy_id == "basic_training"
        
    def test_incremental_training_strategy_initialization(self):
        """Тест инициализации инкрементальной стратегии"""
        strategy = IncrementalTrainingStrategy()
        assert strategy.strategy_id == "incremental_training"
        
    def test_enhanced_optimizer_initialization(self):
        """Тест инициализации оптимизатора"""
        optimizer = EnhancedOptimizer()
        assert optimizer is not None
        
    def test_training_config_validation(self):
        """Тест валидации конфигурации обучения"""
        config = TrainingConfig(
            batch_size=32,
            learning_rate=0.001,
            epochs=10,
            early_stopping_patience=5,
            validation_split=0.2
        )
        
        assert config.batch_size == 32
        assert config.learning_rate == 0.001
        assert config.epochs == 10
        
    def test_callback_functionality(self):
        """Тест callback системы"""
        strategy = BasicTrainingStrategy()
        callback_messages = []
        
        def test_callback(message, progress=None):
            callback_messages.append(message)
        
        strategy.add_callback(test_callback)
        strategy._notify_progress("Test message")
        
        assert "Test message" in callback_messages
        
    def test_training_data_preparation(self):
        """Тест подготовки данных для обучения"""
        strategy = BasicTrainingStrategy()
        
        # Создаем тестовые данные
        test_data = pd.DataFrame(np.random.randn(10, 50))
        data_batch = DataBatch(
            data=test_data,
            batch_id="test_batch",
            data_type=DataType.TRAINING
        )
        
        features, targets = strategy._prepare_training_data(data_batch)
        
        assert features.shape[0] == 10  # batch_size
        assert targets.shape == (10, 4)  # 4 позиции

    @pytest.mark.slow
    def test_basic_training_integration(self):
        """Интеграционный тест базового обучения"""
        # Создаем модель
        model = EnhancedPredictor("test_model")
    
        # Создаем тестовые данные
        test_data = pd.DataFrame(np.random.randn(20, 50))
        data_batch = DataBatch(
            data=test_data,
            batch_id="test_training",
            data_type=DataType.TRAINING
        )
    
        # 🔧 ИСПРАВЛЕНИЕ: Явно инициализируем модель
        model.initialize_model(input_size=50)
    
        # Конфигурация обучения
        config = TrainingConfig(
            batch_size=8,
            learning_rate=0.001,
            epochs=3,  # Мало эпох для теста
            early_stopping_patience=3,
            validation_split=0.2
        )
    
        # Стратегия обучения
        strategy = BasicTrainingStrategy()
    
        # Колбек для отслеживания прогресса
        progress_messages = []
        def progress_callback(message, progress=None):
            progress_messages.append(message)
            print(f"Progress: {message}")
    
        strategy.add_callback(progress_callback)
    
        # Запуск обучения
        result = strategy.train(model, data_batch, config)
    
        # Проверки
        assert result.status.value == "trained"
        assert len(result.training_loss) > 0
        assert result.model_id == "test_model"
        assert len(progress_messages) > 0
        
    def test_optimizer_configuration(self):
        """Тест конфигурации оптимизатора"""
        model = EnhancedPredictor("test_optimizer")
    
        # 🔧 ИСПРАВЛЕНИЕ: Явно инициализируем модель
        model.initialize_model(input_size=50)
    
        config = TrainingConfig(learning_rate=0.001)
        optimizer = EnhancedOptimizer()
    
        configured_optimizer = optimizer.configure_optimizer(model, config)
    
        assert configured_optimizer is not None
        assert hasattr(configured_optimizer, 'param_groups')

if __name__ == "__main__":
    pytest.main([__file__, "-v"])
