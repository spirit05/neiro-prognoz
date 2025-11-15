"""
Интеграционные тесты оркестратора с training стратегиями
"""
import pytest
import pandas as pd
import numpy as np

from ml.core.orchestrator import MLOrchestrator
from ml.core.types import TrainingConfig, DataBatch, DataType
from ml.models.base.enhanced_predictor import EnhancedPredictor


class TestOrchestratorTraining:
    """Тесты интеграции оркестратора с training системой"""
    
    def test_orchestrator_with_basic_training(self):
        """Тест оркестратора с базовой стратегией обучения"""
        # Создаем оркестратор
        orchestrator = MLOrchestrator({})
        
        # Регистрируем модель
        model = EnhancedPredictor("orchestrator_test_model")
        model.initialize_model(input_size=50)
        orchestrator.register_model(model)
        
        # Создаем тестовые данные
        test_data = pd.DataFrame(np.random.randn(20, 50))
        data_batch = DataBatch(
            data=test_data,
            batch_id="orchestrator_test",
            data_type=DataType.TRAINING
        )
        
        # Конфигурация обучения
        config = TrainingConfig(
            batch_size=8,
            learning_rate=0.001,
            epochs=2,  # Мало эпох для теста
            early_stopping_patience=2,
            validation_split=0.2
        )
        
        # Запускаем обучение через оркестратор
        result = orchestrator.train_model_with_strategy(
            model_id="orchestrator_test_model",
            strategy_id="basic",
            data=data_batch,
            config=config
        )
        
        # Проверяем результаты
        assert result.status.value == "trained"
        assert result.model_id == "orchestrator_test_model"
        assert len(result.training_loss) > 0
        
        # Проверяем, что модель обновлена в регистре
        model_info = orchestrator.get_model_info("orchestrator_test_model")
        assert model_info['status'] == result.status
        
    def test_orchestrator_with_unknown_strategy(self):
        """Тест оркестратора с неизвестной стратегией"""
        orchestrator = MLOrchestrator({})
        
        model = EnhancedPredictor("unknown_strategy_test")
        model.initialize_model(input_size=50)
        orchestrator.register_model(model)
        
        test_data = pd.DataFrame(np.random.randn(10, 50))
        data_batch = DataBatch(
            data=test_data,
            batch_id="unknown_strategy_test",
            data_type=DataType.TRAINING
        )
        
        config = TrainingConfig(epochs=1)
        
        # Должна быть ошибка при неизвестной стратегии
        with pytest.raises(ValueError, match="Unknown strategy"):
            orchestrator.train_model_with_strategy(
                model_id="unknown_strategy_test",
                strategy_id="unknown_strategy",
                data=data_batch,
                config=config
            )
