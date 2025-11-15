import pytest
import numpy as np
import pandas as pd
from pathlib import Path
import tempfile

from ml.core.types import DataBatch, TrainingConfig, DataType, ModelStatus
from ml.ensemble import WeightedEnsemblePredictor, StatisticalPredictor, PatternBasedPredictor, FrequencyPredictor


class TestEnsembleSystem:
    def test_ensemble_training(self):
        """Тест обучения ансамбля"""
        ensemble = WeightedEnsemblePredictor("test_ensemble")

        # Создаем тестовые данные
        test_data = np.random.randint(1, 27, (100, 4))
        data_batch = DataBatch(
            data=pd.DataFrame(test_data),  # 🔧 Оборачиваем в DataFrame
            batch_id="test_batch",
            data_type=DataType.TRAINING  # 🔧 Используем enum вместо строки
        )
        
        # Добавляем предсказатели
        statistical = StatisticalPredictor("statistical")
        pattern = PatternBasedPredictor("pattern")
        frequency = FrequencyPredictor("frequency")
        
        ensemble.add_predictor("statistical", statistical, 0.4)
        ensemble.add_predictor("pattern", pattern, 0.3)
        ensemble.add_predictor("frequency", frequency, 0.3)
        
        # Обучаем ансамбль
        result = ensemble.train(data_batch, TrainingConfig(epochs=2))
        
        # Проверяем результат
        assert result.status == ModelStatus.TRAINED
        assert ensemble.is_trained

    def test_ensemble_prediction(self):
        """Тест предсказания ансамбля"""
        ensemble = WeightedEnsemblePredictor("test_ensemble")

        # Создаем тестовые данные для предсказания
        test_data = np.random.randint(1, 27, (50, 4))
        data_batch = DataBatch(
            data=pd.DataFrame(test_data),  # 🔧 Оборачиваем в DataFrame
            batch_id="test_batch",
            data_type=DataType.PREDICTION  # 🔧 Используем enum
        )
        
        # Добавляем предсказатели
        statistical = StatisticalPredictor("statistical")
        pattern = PatternBasedPredictor("pattern")
        
        ensemble.add_predictor("statistical", statistical, 0.5)
        ensemble.add_predictor("pattern", pattern, 0.5)
        
        # Обучаем ансамбль
        train_data = np.random.randint(1, 27, (100, 4))
        train_batch = DataBatch(
            data=pd.DataFrame(train_data),  # 🔧 Оборачиваем в DataFrame
            batch_id="train_batch",
            data_type=DataType.TRAINING
        )
        ensemble.train(train_batch, TrainingConfig(epochs=2))
        
        # Получаем предсказания
        response = ensemble.predict(data_batch)
        
        # Проверяем результат
        assert isinstance(response.predictions, list)
        assert response.model_id == "test_ensemble"

    def test_individual_predictors(self):
        """Тест индивидуальных предсказателей"""
        # Создаем тестовые данные
        test_data = np.random.randint(1, 27, (80, 4))
        data_batch = DataBatch(
            data=pd.DataFrame(test_data),  # 🔧 Оборачиваем в DataFrame
            batch_id="individual_test",
            data_type=DataType.TRAINING  # 🔧 Используем enum
        )
        
        # Тестируем StatisticalPredictor
        statistical = StatisticalPredictor("statistical_test")
        statistical.train(data_batch, TrainingConfig(epochs=2))
        statistical_response = statistical.predict(data_batch)
        assert isinstance(statistical_response.predictions, list)
        
        # Тестируем PatternBasedPredictor
        pattern = PatternBasedPredictor("pattern_test")
        pattern.train(data_batch, TrainingConfig(epochs=2))
        pattern_response = pattern.predict(data_batch)
        assert isinstance(pattern_response.predictions, list)
        
        # Тестируем FrequencyPredictor
        frequency = FrequencyPredictor("frequency_test")
        frequency.train(data_batch, TrainingConfig(epochs=2))
        frequency_response = frequency.predict(data_batch)
        assert isinstance(frequency_response.predictions, list)

    def test_save_load_ensemble(self):
        """Тест сохранения и загрузки ансамбля"""
        with tempfile.TemporaryDirectory() as temp_dir:
            save_path = Path(temp_dir)
            
            ensemble = WeightedEnsemblePredictor("save_test_ensemble")
            
            statistical = StatisticalPredictor("statistical")
            pattern = PatternBasedPredictor("pattern")
            
            ensemble.add_predictor("statistical", statistical, 0.5)
            ensemble.add_predictor("pattern", pattern, 0.5)
            
            # Обучаем на тестовых данных
            test_data = np.random.randint(1, 27, (30, 4))
            data_batch = DataBatch(
                data=pd.DataFrame(test_data),  # 🔧 Оборачиваем в DataFrame
                batch_id="train",
                data_type=DataType.TRAINING
            )
            ensemble.train(data_batch, TrainingConfig(epochs=2))
            
            # Сохраняем
            ensemble.save(save_path)
            
            # Проверяем что файлы созданы
            config_file = save_path / "save_test_ensemble_ensemble_config.json"
            assert config_file.exists()
            
            # Создаем новый ансамбль для загрузки
            new_ensemble = WeightedEnsemblePredictor("save_test_ensemble")
            new_ensemble.add_predictor("statistical", StatisticalPredictor("statistical"), 0.5)
            new_ensemble.add_predictor("pattern", PatternBasedPredictor("pattern"), 0.5)
            
            # Загружаем
            new_ensemble.load(save_path)
            
            # Проверяем что загруженный ансамбль обучен
            assert new_ensemble.is_trained

    def test_prediction_consistency(self):
        """Тест консистентности предсказаний"""
        ensemble = WeightedEnsemblePredictor("consistency_test")
        
        statistical = StatisticalPredictor("statistical")
        pattern = PatternBasedPredictor("pattern")
        
        ensemble.add_predictor("statistical", statistical, 0.5)
        ensemble.add_predictor("pattern", pattern, 0.5)
        
        # Обучаем на тестовых данных
        test_data = np.random.randint(1, 27, (40, 4))
        data_batch = DataBatch(
            data=pd.DataFrame(test_data),  # 🔧 Оборачиваем в DataFrame
            batch_id="train", 
            data_type=DataType.TRAINING
        )
        ensemble.train(data_batch, TrainingConfig(epochs=2))
        
        # Создаем данные для предсказания
        pred_data = np.random.randint(1, 27, (10, 4))
        pred_batch = DataBatch(
            data=pd.DataFrame(pred_data),  # 🔧 Оборачиваем в DataFrame
            batch_id="pred",
            data_type=DataType.PREDICTION
        )
        
        # Получаем два предсказания подряд
        response1 = ensemble.predict(pred_batch)
        response2 = ensemble.predict(pred_batch)
        
        # Проверяем консистентность
        assert len(response1.predictions) == len(response2.predictions)
        assert response1.model_id == response2.model_id
