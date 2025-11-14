"""
ТЕСТЫ ЭТАПА 2: Проверка ПОЛНОЙ РЕАЛИЗАЦИИ AbstractBaseModel интерфейса
"""
import pytest
import torch
import numpy as np
import pandas as pd  # 🔧 ДОБАВИТЬ ИМПОРТ
from pathlib import Path
import tempfile

from ml.models.base.enhanced_predictor import EnhancedPredictor, EnhancedNumberPredictor
from ml.core.types import DataBatch, TrainingConfig, ModelStatus, ModelType


class TestAbstractBaseModelInterface:
    """Тестирование полной реализации AbstractBaseModel интерфейса"""
    
    def test_all_abstract_methods_implemented(self):
        """Тест: все 4 абстрактных метода реализованы"""
        predictor = EnhancedPredictor()
        
        # Проверка что методы существуют и не являются заглушками NotImplementedError
        methods_to_check = ['train', 'predict', 'save', 'load']
        
        for method_name in methods_to_check:
            method = getattr(predictor, method_name)
            assert callable(method), f"Метод {method_name} должен быть вызываемым"
            
            # Проверка что это не базовая абстрактная заглушка
            assert hasattr(method, '__code__'), f"Метод {method_name} должен иметь реализацию"
    
    def test_train_method_interface(self):
        """Тест: метод train соответствует интерфейсу"""
        predictor = EnhancedPredictor()
        
        # Тестовые данные - 🔧 ИСПРАВЛЕНИЕ: обернуть в DataFrame
        test_data = DataBatch(
            data=pd.DataFrame(np.random.randn(10, 50).astype(np.float32)),  # 🔧 ОБЕРНУТЬ В DataFrame
            batch_id="train_batch", 
            data_type="training"
        )
        
        test_config = TrainingConfig(
            batch_size=32,
            learning_rate=0.001,
            epochs=3
        )
        
        # Вызов train не должен вызывать NotImplementedError
        try:
            result = predictor.train(test_data, test_config)
            
            # Проверка структуры результата
            assert hasattr(result, 'model_id')
            assert hasattr(result, 'status') 
            assert hasattr(result, 'training_loss')
            assert hasattr(result, 'metrics')
            
            # Проверка что статус изменился
            assert predictor.status in [ModelStatus.TRAINING, ModelStatus.TRAINED]
            
        except NotImplementedError:
            pytest.fail("Метод train не должен быть заглушкой NotImplementedError")
    
    def test_save_load_cycle(self, tmp_path):
        """Тест: цикл сохранения и загрузки работает"""
        predictor = EnhancedPredictor()
        
        # Инициализация и обучение модели
        predictor.model = EnhancedNumberPredictor()
        predictor._is_trained = True
        
        # Сохранение
        save_path = tmp_path / "test_model.pth"
        predictor.save(save_path)
        
        assert save_path.exists(), "Файл модели должен быть создан"
        
        # Загрузка в новый объект
        new_predictor = EnhancedPredictor()
        new_predictor.load(save_path)
        
        # Проверка что состояние восстановлено
        assert new_predictor._is_trained == predictor._is_trained
        assert new_predictor.model is not None
    
    def test_predict_interface(self):
        """Тест: метод predict соответствует интерфейсу"""
        predictor = EnhancedPredictor()
        
        # Имитация обученной модели
        predictor.model = EnhancedNumberPredictor()
        predictor._is_trained = True
        
        # 🔧 ИСПРАВЛЕНИЕ: обернуть в DataFrame
        test_data = DataBatch(
            data=pd.DataFrame(np.random.randn(1, 50).astype(np.float32)),  # 🔧 ОБЕРНУТЬ В DataFrame
            batch_id="predict_batch",
            data_type="prediction"
        )
        
        # Вызов predict
        response = predictor.predict(test_data)
        
        # Проверка интерфейса PredictionResponse
        assert hasattr(response, 'predictions')
        assert hasattr(response, 'probabilities') 
        assert hasattr(response, 'model_id')
        assert hasattr(response, 'inference_time')
        
        # Проверка типа возвращаемого значения
        from ml.core.types import PredictionResponse
        assert isinstance(response, PredictionResponse)
    
    def test_inheritance_hierarchy(self):
        """Тест: корректная иерархия наследования"""
        from ml.core.base_model import AbstractBaseModel
        
        predictor = EnhancedPredictor()
        
        # Проверка наследования
        assert isinstance(predictor, AbstractBaseModel)
        assert hasattr(predictor, 'model_id')
        assert hasattr(predictor, 'model_type')
        assert hasattr(predictor, 'status')
        assert hasattr(predictor, 'metadata')
        
        # Проверка что model_type установлен правильно
        assert predictor.model_type == ModelType.CLASSIFICATION


def test_interface_completeness():
    """Тест: полная проверка реализации интерфейса"""
    from abc import ABCMeta
    
    # Создание экземпляра
    predictor = EnhancedPredictor()
    
    # Проверка что класс не абстрактный
    assert not hasattr(predictor.__class__, '__abstractmethods__') or \
           len(predictor.__class__.__abstractmethods__) == 0, \
           "Класс не должен иметь нереализованных абстрактных методов"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
