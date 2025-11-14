"""
ИСПРАВЛЕННЫЕ ТЕСТЫ ДЛЯ ЭТАПА 2
"""
import pytest
import torch
import numpy as np
import pandas as pd  # 🔧 ДОБАВИТЬ ИМПОРТ
from pathlib import Path
import tempfile

# 🔧 ИСПРАВЛЕННЫЕ ИМПОРТЫ
from ml.models.base.enhanced_predictor import EnhancedPredictor, EnhancedNumberPredictor
from ml.core.orchestrator import MLOrchestrator
from ml.core.types import DataBatch, TrainingConfig, ModelType, ModelStatus, PredictionResponse  # 🔧 ДОБАВИТЬ PredictionResponse


class TestEnhancedPredictorComplete:
    """Комплексные тесты EnhancedPredictor для ЭТАПА 2"""
    
    def test_abstract_base_model_implementation(self):
        """Тест: полная реализация AbstractBaseModel интерфейса"""
        predictor = EnhancedPredictor()
        
        # Проверка наследования
        from ml.core.base_model import AbstractBaseModel
        assert isinstance(predictor, AbstractBaseModel)
        
        # Проверка что все абстрактные методы реализованы
        methods = ['train', 'predict', 'save', 'load']
        for method in methods:
            assert hasattr(predictor, method)
            assert callable(getattr(predictor, method))
        
        # Проверка что класс не абстрактный
        assert len(getattr(predictor.__class__, '__abstractmethods__', [])) == 0

    def test_new_architecture_components(self):
        """Тест: компоненты новой архитектуры (упрощенной для ЭТАПА 2)"""
        model = EnhancedNumberPredictor(input_size=50, hidden_size=128)
        
        # Проверка наличия компонентов упрощенной архитектуры
        assert hasattr(model, 'network'), "Модель должна иметь network"
        assert isinstance(model.network, torch.nn.Sequential)
        
        # Проверка архитектуры network
        layers = list(model.network)
        assert len(layers) >= 6, "Network должен содержать несколько слоев"
        
        # Проверка forward pass
        batch_size = 3
        test_input = torch.randn(batch_size, 50)
        output = model(test_input)
        assert output.shape == (batch_size, 4, 26)
        assert not torch.isnan(output).any()

    def test_predictor_initialization(self):
        """Тест: инициализация EnhancedPredictor"""
        predictor = EnhancedPredictor(model_id="test_model")
        
        assert predictor.model_id == "test_model"
        assert predictor.model_type == ModelType.CLASSIFICATION
        assert predictor.status == ModelStatus.READY
        assert predictor.input_size == 50
        assert predictor.hidden_size == 128
        assert predictor._is_trained == False

    def test_save_load_cycle(self, tmp_path):
        """Тест: полный цикл сохранения и загрузки"""
        # Создание и обучение модели
        predictor = EnhancedPredictor()
        predictor.model = EnhancedNumberPredictor()
        predictor._is_trained = True
        predictor.status = ModelStatus.TRAINED
        
        # Сохранение
        model_path = tmp_path / "test_model.pth"
        predictor.save(model_path)
        
        assert model_path.exists()
        
        # Проверка содержимого файла
        checkpoint = torch.load(model_path, map_location='cpu', weights_only=False)
        assert 'model_state_dict' in checkpoint
        assert 'model_config' in checkpoint
        assert 'metadata' in checkpoint
        assert checkpoint['is_trained'] == True
        
        # Загрузка в новый объект
        new_predictor = EnhancedPredictor(model_id="loaded_model")
        new_predictor.load(model_path)
        
        # Проверка восстановленного состояния
        assert new_predictor.model_id == "loaded_model"
        assert new_predictor._is_trained == True
        assert new_predictor.status == ModelStatus.READY
        assert new_predictor.model is not None

    def test_training_interface(self):
        """Тест: интерфейс обучения"""
        predictor = EnhancedPredictor()
        
        # Создание тестовых данных
        num_samples = 20
        features = np.random.randn(num_samples, 50).astype(np.float32)
        data_batch = DataBatch(
            data=pd.DataFrame(features),  # 🔧 ИСПРАВЛЕНИЕ: правильное создание DataFrame
            batch_id="test_batch",
            data_type="training"
        )
        
        config = TrainingConfig(
            batch_size=8,
            learning_rate=0.001,
            epochs=3
        )
        
        # Обучение
        result = predictor.train(data_batch, config)
        
        # Проверка результата
        assert result.model_id == predictor.model_id
        assert result.status == ModelStatus.TRAINED
        assert len(result.training_loss) > 0
        assert len(result.validation_loss) > 0
        assert 'final_training_loss' in result.metrics
        
        # Проверка состояния модели
        assert predictor._is_trained == True
        assert predictor.status == ModelStatus.TRAINED

    def test_prediction_interface(self):
        """Тест: интерфейс предсказания"""
        predictor = EnhancedPredictor()
        
        # Имитация обученной модели
        predictor.model = EnhancedNumberPredictor()
        predictor._is_trained = True
        
        # Тестовые данные для предсказания
        features = np.random.randn(5, 50).astype(np.float32)
        data_batch = DataBatch(
            data=pd.DataFrame(features),  # 🔧 ИСПРАВЛЕНИЕ: правильное создание DataFrame
            batch_id="pred_batch", 
            data_type="prediction"
        )
        
        # Предсказание
        response = predictor.predict(data_batch)
        
        # Проверка структуры ответа
        assert isinstance(response, PredictionResponse)
        assert response.model_id == predictor.model_id
        assert isinstance(response.predictions, list)
        assert len(response.predictions) > 0
        assert isinstance(response.probabilities, list)
        
        # Проверка формата прогнозов
        for group in response.predictions:
            assert isinstance(group, tuple)
            assert len(group) == 4
            for number in group:
                assert 1 <= number <= 26

    def test_prediction_validation(self):
        """Тест: валидация прогнозов"""
        predictor = EnhancedPredictor()
        predictor.model = EnhancedNumberPredictor()
        predictor._is_trained = True
        
        # Тестовые данные
        features = np.random.randn(1, 50).astype(np.float32)
        data_batch = DataBatch(
            data=pd.DataFrame(features),  # 🔧 ИСПРАВЛЕНИЕ: правильное создание DataFrame
            batch_id="valid_batch",
            data_type="prediction" 
        )
        
        response = predictor.predict(data_batch)
        
        # Проверка что все прогнозы валидны
        for group in response.predictions:
            # Проверка уникальности в парах
            assert group[0] != group[1], f"Невалидная первая пара: {group}"
            assert group[2] != group[3], f"Невалидная вторая пара: {group}"
            
            # Проверка что не все числа одинаковые
            assert len(set(group)) >= 2, f"Все числа одинаковые: {group}"

    def test_feature_size_adaptation(self):
        """Тест: адаптация размера features"""
        predictor = EnhancedPredictor()
        
        # Тест с меньшим количеством features
        small_features = np.random.randn(10, 30).astype(np.float32)
        adapted = predictor._adapt_features_size(small_features)
        assert adapted.shape == (10, 50)
        assert np.all(adapted[:, 30:] == 0)  # Дополнены нулями
        
        # Тест с большим количеством features  
        large_features = np.random.randn(10, 70).astype(np.float32)
        adapted = predictor._adapt_features_size(large_features)
        assert adapted.shape == (10, 50)
        assert np.array_equal(adapted, large_features[:, :50])  # Обрезаны

    def test_integration_with_orchestrator(self):
        """Тест: интеграция с MLOrchestrator"""
        orchestrator = MLOrchestrator({"debug": True})
        predictor = EnhancedPredictor(model_id="orchestrator_test")
        
        # Регистрация модели
        orchestrator.register_model(predictor)
        
        # Проверка регистрации
        models = orchestrator.list_models()
        assert len(models) == 1
        assert models[0]['model_id'] == "orchestrator_test"
        assert models[0]['model_type'] == "classification"
        
        # Получение информации о модели
        model_info = orchestrator.get_model_info("orchestrator_test")
        assert model_info is not None
        assert model_info['model_id'] == "orchestrator_test"
        assert 'metadata' in model_info

    def test_model_info(self):
        """Тест: информация о модели"""
        predictor = EnhancedPredictor()
        info = predictor.get_model_info()
        
        expected_keys = [
            'model_id', 'architecture', 'input_size', 'hidden_size',
            'is_trained', 'status', 'feature_specs_count'
        ]
        
        for key in expected_keys:
            assert key in info
        
        assert info['architecture'] == 'EnhancedNumberPredictor (совместимая с оригиналом)'
        # Убрали проверки на has_cnn_branch и has_mlp_branch

    def test_error_handling(self):
        """Тест: обработка ошибок"""
        predictor = EnhancedPredictor()
        
        # Попытка предсказания без обучения
        data_batch = DataBatch(
            data=pd.DataFrame(np.random.randn(1, 50)),  # 🔧 ИСПРАВЛЕНИЕ: правильное создание DataFrame
            batch_id="error_batch",
            data_type="prediction"
        )
        
        with pytest.raises(ValueError, match="Модель не обучена"):
            predictor.predict(data_batch)
        
        # Попытка сохранения без инициализации модели
        with tempfile.TemporaryDirectory() as temp_dir:
            model_path = Path(temp_dir) / "model.pth"
            with pytest.raises(ValueError, match="Модель не инициализирована"):
                predictor.save(model_path)

    def test_prediction_consistency(self):
        """Тест: консистентность прогнозов"""
        predictor = EnhancedPredictor()
        predictor.model = EnhancedNumberPredictor()
        predictor._is_trained = True
        
        # Одни и те же данные должны давать одинаковые результаты при одинаковой модели
        features = np.random.randn(1, 50).astype(np.float32)
        data_batch = DataBatch(
            data=pd.DataFrame(features),  # 🔧 ИСПРАВЛЕНИЕ: правильное создание DataFrame
            batch_id="consistency_batch",
            data_type="prediction"
        )
        
        response1 = predictor.predict(data_batch)
        response2 = predictor.predict(data_batch)
        
        # Прогнозы должны быть одинаковыми (при выключенном dropout)
        assert response1.predictions == response2.predictions


def test_import_compatibility():
    """Тест: совместимость импортов"""
    # Все эти импорты должны работать без ошибок
    from ml.models.base import EnhancedPredictor
    from ml.models.base.enhanced_predictor import EnhancedNumberPredictor
    from ml.core.base_model import AbstractBaseModel
    from ml.core.types import ModelType, DataBatch
    assert True


if __name__ == "__main__":
    # Запуск тестов
    pytest.main([__file__, "-v", "--tb=short"])

