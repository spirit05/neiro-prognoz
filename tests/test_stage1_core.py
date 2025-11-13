"""
Тесты для ЭТАПА 1: Базовые абстракции и types
"""
import pytest
import pandas as pd
import numpy as np
from datetime import datetime
from pathlib import Path

from ml.core.types import (
    ModelType, ModelStatus, TrainingConfig, ModelMetadata,
    DataBatch, FeatureSpec, PredictionRequest
)
from ml.core.base_model import AbstractBaseModel
from ml.core.orchestrator import MLOrchestrator


class TestMockModel(AbstractBaseModel):
    """Mock модель для тестирования абстрактных классов"""
    
    def __init__(self, model_id: str, model_type: ModelType):
        super().__init__(model_id, model_type)
        self._feature_specs = [
            FeatureSpec(name="feature1", dtype="float64", required=True),
            FeatureSpec(name="feature2", dtype="int64", required=False)
        ]

    def train(self, data, config):
        return TrainingResult(
            model_id=self.model_id,
            status=ModelStatus.TRAINED,
            training_loss=[0.5, 0.3, 0.1],
            validation_loss=[0.6, 0.4, 0.2],
            metrics={"accuracy": 0.95, "loss": 0.1},
            training_time=10.5,
            best_epoch=3
        )

    def predict(self, data):
        return PredictionResponse(
            predictions=[1, 0, 1],
            model_id=self.model_id,
            inference_time=0.1
        )

    def save(self, path):
        pass

    def load(self, path):
        self._is_trained = True


class TestTypes:
    """Тесты для типов данных"""
    
    def test_model_types_enum(self):
        """Тест enum типов моделей"""
        assert ModelType.REGRESSION == "regression"
        assert ModelType.CLASSIFICATION == "classification"
        
    def test_training_config_validation(self):
        """Тест валидации конфигурации обучения"""
        config = TrainingConfig(
            batch_size=32,
            learning_rate=0.001,
            epochs=100
        )
        assert config.batch_size == 32
        assert config.learning_rate == 0.001
        
        with pytest.raises(ValueError):
            TrainingConfig(batch_size=0)  # Должно быть >= 1
            
    def test_model_metadata(self):
        """Тест метаданных модели"""
        metadata = ModelMetadata(
            model_id="test_model",
            model_type=ModelType.REGRESSION,
            features=["feature1", "feature2"],
            target_columns=["target"]
        )
        assert metadata.model_id == "test_model"
        assert metadata.features == ["feature1", "feature2"]
        
    def test_data_batch(self):
        """Тест пакета данных"""
        df = pd.DataFrame({"feature1": [1, 2, 3], "feature2": [4, 5, 6]})
        batch = DataBatch(
            data=df,
            batch_id="test_batch",
            data_type="training"
        )
        assert batch.batch_id == "test_batch"
        assert len(batch.data) == 3


class TestBaseModel:
    """Тесты базовой модели"""
    
    def test_abstract_base_model_initialization(self):
        """Тест инициализации абстрактной модели"""
        model = TestMockModel("test_model", ModelType.REGRESSION)
        
        assert model.model_id == "test_model"
        assert model.model_type == ModelType.REGRESSION
        assert model.status == ModelStatus.READY
        assert not model.is_trained
        
    def test_feature_validation(self):
        """Тест валидации фич"""
        model = TestMockModel("test_model", ModelType.REGRESSION)
        
        # Валидные данные
        valid_data = pd.DataFrame({
            "feature1": [1.0, 2.0, 3.0],
            "feature2": [1, 2, 3]
        })
        assert model.validate_features(valid_data) == True
        
        # Невалидные данные - отсутствует обязательная фича
        invalid_data = pd.DataFrame({
            "feature2": [1, 2, 3]  # Нет feature1
        })
        assert model.validate_features(invalid_data) == False
        
    def test_metadata_update(self):
        """Тест обновления метаданных"""
        model = TestMockModel("test_model", ModelType.REGRESSION)
        
        model.update_metadata(version="2.0.0", features=["new_feature"])
        assert model.metadata.version == "2.0.0"
        assert model.metadata.features == ["new_feature"]


class TestOrchestrator:
    """Тесты оркестратора"""
    
    def test_orchestrator_initialization(self):
        """Тест инициализации оркестратора"""
        orchestrator = MLOrchestrator({"debug": True})
        assert orchestrator.config == {"debug": True}
        assert len(orchestrator.list_models()) == 0
        
    def test_model_registration(self):
        """Тест регистрации модели"""
        orchestrator = MLOrchestrator({})
        model = TestMockModel("test_model", ModelType.REGRESSION)
        
        orchestrator.register_model(model)
        models = orchestrator.list_models()
        
        assert len(models) == 1
        assert models[0]['model_id'] == "test_model"
        assert models[0]['model_type'] == "regression"
        
    def test_get_model_info(self):
        """Тест получения информации о модели"""
        orchestrator = MLOrchestrator({})
        model = TestMockModel("test_model", ModelType.REGRESSION)
        
        orchestrator.register_model(model)
        info = orchestrator.get_model_info("test_model")
        
        assert info is not None
        assert info['model_id'] == "test_model"
        assert 'metadata' in info


def test_imports():
    """Тест что все модули импортируются без ошибок"""
    from ml.core import types, base_model, orchestrator
    from ml.core.types import ModelType, TrainingConfig
    from ml.core.base_model import AbstractBaseModel
    from ml.core.orchestrator import MLOrchestrator
    
    assert True  # Если импорты прошли без ошибок

