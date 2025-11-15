# /opt/model/tests/test_stage5_ensemble.py
"""
ТЕСТЫ ЭТАПА 5: Ансамблевая система - ЧИСТАЯ АРХИТЕКТУРА
"""

import pytest
import numpy as np
from pathlib import Path
import tempfile

from ml.core.types import DataBatch, TrainingConfig
from ml.ensemble import (
    WeightedEnsemblePredictor, StatisticalPredictor, 
    PatternBasedPredictor, FrequencyPredictor, EnsembleFactory
)


class TestEnsembleSystem:
    """Тесты ансамблевой системы"""
    
    def test_ensemble_initialization(self):
        """Тест инициализации ансамбля"""
        ensemble = WeightedEnsemblePredictor("test_ensemble")
        
        assert ensemble.model_id == "test_ensemble"
        assert len(ensemble.component_predictors) == 0
        assert len(ensemble.weights) == 0
        assert not ensemble._prediction_lock
    
    def test_add_predictors(self):
        """Тест добавления предсказателей в ансамбль"""
        ensemble = WeightedEnsemblePredictor("test_ensemble")
        
        statistical = StatisticalPredictor("statistical")
        pattern = PatternBasedPredictor("pattern")
        
        ensemble.add_predictor("statistical", statistical, 0.4)
        ensemble.add_predictor("pattern", pattern, 0.3)
        
        assert "statistical" in ensemble.component_predictors
        assert "pattern" in ensemble.component_predictors
        assert ensemble.weights["statistical"] == 0.4
        assert ensemble.weights["pattern"] == 0.3
    
    def test_ensemble_training(self):
        """Тест обучения ансамбля"""
        ensemble = WeightedEnsemblePredictor("test_ensemble")
        
        # Создаем тестовые данные
        test_data = np.random.randint(1, 27, (100, 4))
        data_batch = DataBatch(
            data=test_data,
            batch_id="test_batch",
            data_type="training"
        )
        
        config = TrainingConfig(
            batch_size=32,
            learning_rate=0.001,
            epochs=10
        )
        
        # Добавляем предсказатели
        statistical = StatisticalPredictor("statistical")
        pattern = PatternBasedPredictor("pattern")
        
        ensemble.add_predictor("statistical", statistical, 0.5)
        ensemble.add_predictor("pattern", pattern, 0.5)
        
        # Обучаем ансамбль
        result = ensemble.train(data_batch, config)
        
        assert result.status.value == "trained"
        assert ensemble.is_trained
        assert statistical.is_trained
        assert pattern.is_trained
    
    def test_ensemble_prediction(self):
        """Тест предсказания ансамбля"""
        ensemble = WeightedEnsemblePredictor("test_ensemble")
        
        # Создаем тестовые данные для предсказания
        test_data = np.random.randint(1, 27, (50, 4))
        data_batch = DataBatch(
            data=test_data,
            batch_id="test_batch",
            data_type="prediction"
        )
        
        # Добавляем и обучаем предсказатели
        statistical = StatisticalPredictor("statistical")
        pattern = PatternBasedPredictor("pattern")
        
        ensemble.add_predictor("statistical", statistical, 0.6)
        ensemble.add_predictor("pattern", pattern, 0.4)
        
        # Обучаем на тех же данных
        train_data = DataBatch(
            data=test_data,
            batch_id="train_batch", 
            data_type="training"
        )
        
        config = TrainingConfig(epochs=5)
        ensemble.train(train_data, config)
        
        # Тестируем предсказание
        response = ensemble.predict(data_batch)
        
        assert response.model_id == "test_ensemble"
        assert isinstance(response.predictions, list)
        assert len(response.predictions) > 0
    
    def test_individual_predictors(self):
        """Тест индивидуальных предсказателей"""
        # Тестируем StatisticalPredictor
        statistical = StatisticalPredictor("statistical_test")
        test_data = np.random.randint(1, 27, (30, 4))
        data_batch = DataBatch(data=test_data, batch_id="test", data_type="training")
        
        result = statistical.train(data_batch, TrainingConfig(epochs=5))
        assert statistical.is_trained
        
        prediction = statistical.predict(data_batch)
        assert isinstance(prediction.predictions, list)
        
        # Тестируем PatternBasedPredictor
        pattern = PatternBasedPredictor("pattern_test")
        result = pattern.train(data_batch, TrainingConfig(epochs=5))
        assert pattern.is_trained
        
        prediction = pattern.predict(data_batch)
        assert isinstance(prediction.predictions, list)
        
        # Тестируем FrequencyPredictor
        frequency = FrequencyPredictor("frequency_test")
        result = frequency.train(data_batch, TrainingConfig(epochs=5))
        assert frequency.is_trained
        
        prediction = frequency.predict(data_batch)
        assert isinstance(prediction.predictions, list)
    
    def test_save_load_ensemble(self):
        """Тест сохранения и загрузки ансамбля"""
        with tempfile.TemporaryDirectory() as temp_dir:
            save_path = Path(temp_dir)
            
            # Создаем и обучаем ансамбль
            ensemble = WeightedEnsemblePredictor("save_test_ensemble")
            
            statistical = StatisticalPredictor("statistical")
            pattern = PatternBasedPredictor("pattern")
            
            ensemble.add_predictor("statistical", statistical, 0.5)
            ensemble.add_predictor("pattern", pattern, 0.5)
            
            # Обучаем на тестовых данных
            test_data = np.random.randint(1, 27, (50, 4))
            data_batch = DataBatch(data=test_data, batch_id="train", data_type="training")
            ensemble.train(data_batch, TrainingConfig(epochs=5))
            
            # Сохраняем
            ensemble.save(save_path)
            
            # Создаем новый ансамбль и загружаем
            new_ensemble = WeightedEnsemblePredictor("save_test_ensemble")
            new_ensemble.add_predictor("statistical", StatisticalPredictor("statistical"), 0.5)
            new_ensemble.add_predictor("pattern", PatternBasedPredictor("pattern"), 0.5)
            
            new_ensemble.load(save_path)
            
            assert new_ensemble.is_trained
            assert new_ensemble.weights["statistical"] == 0.5
            assert new_ensemble.weights["pattern"] == 0.5
    
    def test_ensemble_factory(self):
        """Тест фабрики создания ансамбля"""
        config = {
            'ensemble': {
                'model_id': 'factory_test_ensemble',
                'combiners': {
                    'weighted': {
                        'params': {
                            'weights': {
                                'statistical': 0.4,
                                'pattern': 0.3,
                                'frequency': 0.3
                            }
                        }
                    }
                },
                'predictors': {
                    'statistical': {
                        'class': 'ml.ensemble.predictors.statistical.StatisticalPredictor',
                        'params': {'model_id': 'statistical_factory'}
                    },
                    'pattern': {
                        'class': 'ml.ensemble.predictors.pattern_based.PatternBasedPredictor',
                        'params': {'model_id': 'pattern_factory'}
                    },
                    'frequency': {
                        'class': 'ml.ensemble.predictors.frequency.FrequencyPredictor', 
                        'params': {'model_id': 'frequency_factory'}
                    }
                }
            }
        }
        
        ensemble = EnsembleFactory.create_from_config(config)
        
        assert ensemble.model_id == "factory_test_ensemble"
        assert "statistical" in ensemble.component_predictors
        assert "pattern" in ensemble.component_predictors  
        assert "frequency" in ensemble.component_predictors
        assert ensemble.weights["statistical"] == 0.4
        assert ensemble.weights["pattern"] == 0.3
        assert ensemble.weights["frequency"] == 0.3
    
    def test_prediction_consistency(self):
        """Тест консистентности предсказаний"""
        ensemble = WeightedEnsemblePredictor("consistency_test")
        
        statistical = StatisticalPredictor("statistical")
        pattern = PatternBasedPredictor("pattern")
        
        ensemble.add_predictor("statistical", statistical, 0.5)
        ensemble.add_predictor("pattern", pattern, 0.5)
        
        # Обучаем на тестовых данных
        test_data = np.random.randint(1, 27, (40, 4))
        data_batch = DataBatch(data=test_data, batch_id="train", data_type="training")
        ensemble.train(data_batch, TrainingConfig(epochs=5))
        
        # Тестовые данные для предсказания
        pred_data = DataBatch(
            data=np.random.randint(1, 27, (10, 4)),
            batch_id="pred",
            data_type="prediction"
        )
        
        # Многократные предсказания должны быть консистентными
        response1 = ensemble.predict(pred_data)
        response2 = ensemble.predict(pred_data)
        
        # Проверяем, что структура ответов одинаковая
        assert len(response1.predictions) == len(response2.predictions)
        assert isinstance(response1.predictions, type(response2.predictions))


def test_ensemble_integration_with_orchestrator():
    """Тест интеграции ансамбля с MLOrchestrator"""
    from ml.core.orchestrator import MLOrchestrator
    
    # Создаем оркестратор
    orchestrator = MLOrchestrator({})
    
    # Создаем и регистрируем ансамбль
    ensemble = WeightedEnsemblePredictor("orchestrator_test")
    statistical = StatisticalPredictor("statistical")
    pattern = PatternBasedPredictor("pattern")
    
    ensemble.add_predictor("statistical", statistical, 0.6)
    ensemble.add_predictor("pattern", pattern, 0.4)
    
    orchestrator.register_model(ensemble)
    
    # Проверяем регистрацию
    model_info = orchestrator.get_model_info("orchestrator_test")
    assert model_info is not None
    assert model_info['model_id'] == "orchestrator_test"
    
    # Проверяем список моделей
    models = orchestrator.list_models()
    assert len(models) == 1
    assert models[0]['model_id'] == "orchestrator_test"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
