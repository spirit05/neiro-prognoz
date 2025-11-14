"""
ТЕСТЫ ЭТАПА 2: Минимальная проверка идентичности прогнозов
"""
import pytest
import torch
import numpy as np
import pandas as pd  # 🔧 ДОБАВИТЬ ИМПОРТ
from pathlib import Path

from ml.models.base.enhanced_predictor import EnhancedPredictor, EnhancedNumberPredictor
from ml.core.types import DataBatch


class TestStage2Minimal:
    """Минимальные тесты для проверки ЭТАПА 2"""
    
    def test_model_architecture_identical(self):
        """Тест: архитектура модели идентична оригинальной"""
        model = EnhancedNumberPredictor(input_size=50, hidden_size=128)
        
        # Проверка архитектуры
        assert hasattr(model, 'network')
        assert isinstance(model.network, torch.nn.Sequential)
        assert model.input_size == 50
        assert model.hidden_size == 128
        
        # Проверка forward pass
        test_input = torch.randn(2, 50)
        output = model(test_input)
        assert output.shape == (2, 4, 26)
    
    def test_predictor_loads_original_weights(self, tmp_path):
        """Тест: загрузка оригинальных весов .pth файла"""
        # Создаем тестовый файл весов
        test_weights = {
            'model_state_dict': EnhancedNumberPredictor().state_dict(),
            'model_config': {'input_size': 50, 'hidden_size': 128},
            'is_trained': True,  # 🔧 ДОБАВИТЬ ЭТОТ КЛЮЧ
            'model_type': 'classification'  # 🔧 ДОБАВИТЬ ДЛЯ СОВМЕСТИМОСТИ
        }
        
        weights_path = tmp_path / "test_weights.pth"
        torch.save(test_weights, weights_path)
        
        # Загрузка через новый Predictor
        predictor = EnhancedPredictor()
        predictor.load(weights_path)
        
        assert predictor.is_trained == True
        assert predictor.model is not None
    
    def test_predictions_format_identical(self):
        """Тест: формат прогнозов идентичен оригинальному"""
        predictor = EnhancedPredictor()
        
        # Имитация загруженной модели
        predictor.model = EnhancedNumberPredictor()
        predictor._is_trained = True
        
        # Тестовые данные - 🔧 ИСПРАВЛЕНИЕ: обернуть в DataFrame
        test_data = DataBatch(
            data=pd.DataFrame(np.random.randn(1, 50).astype(np.float32)),  # 🔧 ОБЕРНУТЬ В DataFrame
            batch_id="test_batch",
            data_type="prediction"
        )
        
        # Предсказание
        response = predictor.predict(test_data)
        
        # Проверка формата ответа
        assert hasattr(response, 'predictions')
        assert hasattr(response, 'probabilities')
        assert hasattr(response, 'model_id')
        assert len(response.predictions) > 0
        
        # Каждая группа должна иметь 4 числа
        for group in response.predictions:
            assert len(group) == 4
            assert all(1 <= x <= 26 for x in group)


def test_imports_work():
    """Тест: все модули импортируются без ошибок"""
    # Пробуем разные варианты импорта
    try:
        from ml.models.base.enhanced_predictor import EnhancedPredictor
        from ml.models.base.enhanced_predictor import EnhancedNumberPredictor
        assert True
    except ImportError as e:
        pytest.fail(f"Импорт не работает: {e}")


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
