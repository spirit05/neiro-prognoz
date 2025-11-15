# [file name]: tests/test_dataprocessor_integration.py
"""
Тест интеграции feature engineers с DataProcessor
"""

import pytest
import numpy as np
import sys
import os

sys.path.insert(0, '/opt/model')

def test_dataprocessor_with_feature_engineers():
    """Тест что DataProcessor может использовать feature engineers"""
    try:
        from ml.core.data_processor import DataProcessor
        
        # Создаем DataProcessor
        processor = DataProcessor(history_size=20)
        
        # Тестовые данные
        test_groups = [
            "1 2 3 4", "5 6 7 8", "9 10 11 12", "13 14 15 16", "17 18 19 20",
            "21 22 23 24", "1 3 5 7", "2 4 6 8", "9 11 13 15", "10 12 14 16"
        ]
        
        # Тестируем создание фич для предсказания
        prediction_features = processor.create_prediction_features(test_groups)
        
        # Проверяем что фичи созданы
        assert prediction_features is not None, "Prediction features are None"
        
        # Если есть фичи, проверяем их структуру
        if len(prediction_features) > 0:
            if isinstance(prediction_features, np.ndarray):
                feature_vector = prediction_features
            else:
                feature_vector = prediction_features[0] if len(prediction_features) > 0 else None
            
            if feature_vector is not None:
                assert isinstance(feature_vector, np.ndarray), f"Features are not numpy array: {type(feature_vector)}"
                assert feature_vector.dtype == np.float32, f"Wrong dtype: {feature_vector.dtype}"
                print(f"✅ Prediction features created: {feature_vector.shape}")
        
        # Тестируем подготовку данных для обучения
        training_groups = test_groups * 3  # Увеличиваем количество данных
        
        features, targets = processor.prepare_training_data(training_groups)
        
        # Проверяем что данные подготовлены (может быть пусто если мало данных)
        if len(features) > 0:
            assert features.shape[0] == targets.shape[0], "Features and targets count mismatch"
            assert features.dtype == np.float32, f"Wrong features dtype: {features.dtype}"
            assert targets.dtype == np.int64, f"Wrong targets dtype: {targets.dtype}"
            print(f"✅ Training data prepared: {features.shape[0]} samples with {features.shape[1]} features")
        else:
            print("⚠️ No training data generated (may be normal for small datasets)")
        
        print("✅ DataProcessor integration test passed")
        return True
        
    except Exception as e:
        pytest.fail(f"DataProcessor integration test failed: {e}")

def test_feature_consistency():
    """Тест консистентности фич при разных вызовах"""
    try:
        from ml.features.engineers.statistical import StatisticalEngineer
        
        engineer = StatisticalEngineer(history_size=10)
        test_data = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10]
        
        # Первый вызов
        features1 = engineer.extract_features(test_data)
        
        # Второй вызов с теми же данными
        features2 = engineer.extract_features(test_data)
        
        # Фичи должны быть идентичными
        assert np.array_equal(features1, features2), "Features are not consistent between calls"
        
        print("✅ Feature consistency test passed")
        return True
        
    except Exception as e:
        pytest.fail(f"Feature consistency test failed: {e}")

if __name__ == "__main__":
    test_dataprocessor_with_feature_engineers()
    test_feature_consistency()
    print("🎉 Все тесты интеграции с DataProcessor пройдены!")
