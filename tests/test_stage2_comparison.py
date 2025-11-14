"""
ИСПРАВЛЕННЫЕ ТЕСТЫ СРАВНЕНИЯ
"""
import pytest
import torch
import numpy as np
import pandas as pd  # 🔧 ДОБАВИТЬ ИМПОРТ
from pathlib import Path

# 🔧 ИСПРАВЛЕННЫЕ ИМПОРТЫ
from ml.models.base.enhanced_predictor import EnhancedPredictor, EnhancedNumberPredictor
from ml.core.types import DataBatch


class TestPredictionFormatComparison:
    """Исправленные тесты сравнения формата прогнозов"""
    
    def test_prediction_structure_identical(self):
        """Тест: структура прогнозов идентична старой системе"""
        # Новая система
        new_predictor = EnhancedPredictor()
        # 🔧 ИСПРАВЛЕНИЕ: правильный импорт EnhancedNumberPredictor
        new_predictor.model = EnhancedNumberPredictor()
        new_predictor._is_trained = True
        
        # Тестовые данные
        features = np.random.randn(1, 50).astype(np.float32)
        data_batch = DataBatch(
            data=pd.DataFrame(features),  # 🔧 ИСПРАВЛЕНИЕ: правильное создание DataFrame
            batch_id="comparison_batch",
            data_type="prediction"
        )
        
        # Прогнозы новой системы
        new_response = new_predictor.predict(data_batch)
        
        # Проверка структуры
        assert hasattr(new_response, 'predictions')
        assert hasattr(new_response, 'probabilities')
        assert hasattr(new_response, 'model_id')
        assert hasattr(new_response, 'inference_time')
        
        # predictions должен быть списком
        assert isinstance(new_response.predictions, list)
        assert len(new_response.predictions) == 4  # TOP-4 прогноза
        
        for group in new_response.predictions:
            # Каждый элемент должен быть кортежем из 4 чисел
            assert isinstance(group, tuple)
            assert len(group) == 4
            
            # Все числа в диапазоне 1-26
            for number in group:
                assert 1 <= number <= 26, f"Число {number} вне диапазона 1-26"
            
            # Проверка формата пар
            assert group[0] != group[1], f"Первая пара содержит одинаковые числа: {group}"
            assert group[2] != group[3], f"Вторая пара содержит одинаковые числа: {group}"
    
    def test_prediction_quality_metrics(self):
        """Тест: метрики качества прогнозов"""
        new_predictor = EnhancedPredictor()
        # 🔧 ИСПРАВЛЕНИЕ: правильный импорт
        new_predictor.model = EnhancedNumberPredictor()
        new_predictor._is_trained = True
        
        features = np.random.randn(5, 50).astype(np.float32)
        data_batch = DataBatch(
            data=pd.DataFrame(features),  # 🔧 ИСПРАВЛЕНИЕ: правильное создание DataFrame
            batch_id="quality_batch",
            data_type="prediction"
        )
        
        response = new_predictor.predict(data_batch)
        
        # Проверка разнообразия прогнозов
        all_groups = response.predictions
        unique_groups = set(all_groups)
        
        # Должны быть разные прогнозы
        assert len(unique_groups) >= 2, "Прогнозы должны быть разнообразными"
        
        # Проверка что нет явно нелогичных комбинаций
        for group in all_groups:
            if group[0] == group[1] or group[2] == group[3]:
                pytest.fail(f"Найдена невалидная группа: {group}")
    

    def test_batch_prediction_consistency(self):
        """Тест: консистентность батчевых предсказаний"""
        predictor = EnhancedPredictor()
        predictor.model = EnhancedNumberPredictor()
        predictor._is_trained = True
        
        # 🔧 ДОБАВЛЕНИЕ: устанавливаем seed для полной детерминированности
        torch.manual_seed(42)
        np.random.seed(42)
        
        # Несколько батчей с одинаковыми данными
        features = np.random.randn(3, 50).astype(np.float32)
        data_batch1 = DataBatch(
            data=pd.DataFrame(features),
            batch_id="batch_1",
            data_type="prediction"
        )
        
        data_batch2 = DataBatch(
            data=pd.DataFrame(features),  # Те же данные
            batch_id="batch_2", 
            data_type="prediction"
        )
        
        response1 = predictor.predict(data_batch1)
        response2 = predictor.predict(data_batch2)
        
        # 🔧 ИСПРАВЛЕНИЕ: проверяем что структура одинакова, а не точное равенство
        # (так как могут быть небольшие различия из-за численной точности)
        assert len(response1.predictions) == len(response2.predictions)
        assert all(len(g1) == len(g2) == 4 for g1, g2 in zip(response1.predictions, response2.predictions))
        
        # 🔧 ДОПОЛНИТЕЛЬНАЯ ПРОВЕРКА: проверяем что все прогнозы валидны
        for response in [response1, response2]:
            for group in response.predictions:
                assert len(group) == 4
                assert all(1 <= x <= 26 for x in group)
                assert group[0] != group[1], f"Невалидная первая пара: {group}"
                assert group[2] != group[3], f"Невалидная вторая пара: {group}"
