"""
ТЕСТЫ ЭТАПА 2: Проверка архитектуры модели (упрощенная для ЭТАПА 2)
"""
import pytest
import torch
import numpy as np
import pandas as pd
from pathlib import Path

from ml.models.base.enhanced_predictor import EnhancedPredictor, EnhancedNumberPredictor
from ml.core.types import DataBatch


class TestEnhancedArchitecture:
    """Тестирование архитектуры модели"""
    
    def test_architecture_components(self):
        """Тест: компоненты архитектуры"""
        model = EnhancedNumberPredictor(input_size=50, hidden_size=128)
        
        # Проверка наличия компонентов архитектуры
        assert hasattr(model, 'network'), "Модель должна иметь network"
        
        # Проверка архитектуры network
        layers = list(model.network)
        assert len(layers) >= 6, "Network должен содержать несколько слоев"
    
    def test_forward_pass(self):
        """Тест: forward pass архитектуры"""
        model = EnhancedNumberPredictor(input_size=50, hidden_size=128)
        model.eval()
        
        # Тестовый вход
        batch_size = 2
        input_tensor = torch.randn(batch_size, 50)
        
        with torch.no_grad():
            output = model(input_tensor)
        
        # Проверка выходной формы
        assert output.shape == (batch_size, 4, 26), f"Ожидалась форма (2, 4, 26), получено {output.shape}"
        
        # Проверка что нет NaN значений
        assert not torch.isnan(output).any(), "Выход содержит NaN значения"
        
        # Проверка что вероятности в разумном диапазоне
        probabilities = torch.softmax(output, dim=-1)
        assert torch.all(probabilities >= 0), "Вероятности должны быть неотрицательными"
        assert torch.all(probabilities <= 1), "Вероятности должны быть <= 1"
    
    def test_predictor_with_architecture(self):
        """Тест: EnhancedPredictor с архитектурой"""
        predictor = EnhancedPredictor()
        
        # Проверка информации о модели
        model_info = predictor.get_model_info()
        assert model_info['architecture'] == 'EnhancedNumberPredictor (совместимая с оригиналом)'
    
    def test_prediction_format_with_architecture(self):
        """Тест: формат прогнозов с архитектурой"""
        predictor = EnhancedPredictor()
        
        # Имитация загруженной модели
        predictor.model = EnhancedNumberPredictor()
        predictor._is_trained = True
        
        # Тестовые данные
        test_data = DataBatch(
            data=pd.DataFrame(np.random.randn(1, 50).astype(np.float32)),
            batch_id="test_batch",
            data_type="prediction"
        )
        
        # Предсказание
        response = predictor.predict(test_data)
        
        # Проверка формата ответа
        assert hasattr(response, 'predictions'), "Ответ должен содержать predictions"
        assert hasattr(response, 'probabilities'), "Ответ должен содержать probabilities"
        assert hasattr(response, 'model_id'), "Ответ должен содержать model_id"
        
        # Проверка структуры прогнозов
        assert len(response.predictions) > 0, "Должен быть хотя бы один прогноз"
        
        for group in response.predictions:
            assert len(group) == 4, f"Группа должна содержать 4 числа, получено {len(group)}"
            assert all(1 <= x <= 26 for x in group), f"Числа должны быть в диапазоне 1-26, получено {group}"
            
            # Проверка уникальности в парах
            assert group[0] != group[1], f"Первая пара не должна содержать одинаковые числа: {group}"
            assert group[2] != group[3], f"Вторая пара не должна содержать одинаковые числа: {group}"


def test_architecture_comparison():
    """Сравнение архитектуры"""
    # Архитектура
    model = EnhancedNumberPredictor(input_size=50, hidden_size=128)
    
    # Проверка что архитектура имеет ожидаемые компоненты
    assert hasattr(model, 'network'), "Архитектура должна иметь network"
    
    # 🔧 ИСПРАВЛЕНИЕ: обновляем ожидания для упрощенной архитектуры
    params = sum(p.numel() for p in model.parameters())
    assert params > 30000, f"Архитектура должна иметь достаточно параметров, получено {params}"
    assert params < 50000, f"Упрощенная архитектура должна иметь меньше параметров, получено {params}"
    
    # 🔧 ДОПОЛНИТЕЛЬНАЯ ПРОВЕРКА: проверяем конкретные слои
    layers = list(model.network)
    linear_layers = [layer for layer in layers if isinstance(layer, torch.nn.Linear)]
    assert len(linear_layers) == 4, f"Должно быть 4 линейных слоя, найдено {len(linear_layers)}"

if __name__ == "__main__":
    pytest.main([__file__, "-v"])
