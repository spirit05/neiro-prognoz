# [file name]: tests/test_dataprocessor_compatibility.py
"""
Тест совместимости feature engineers с будущим DataProcessor
Проверяет, что feature engineers готовы к интеграции без фактического использования DataProcessor
"""

import pytest
import numpy as np
import sys
import os

sys.path.insert(0, '/opt/model')

def test_feature_engineers_ready_for_dataprocessor():
    """Тест что feature engineers готовы к интеграции с DataProcessor"""
    try:
        from ml.features.engineers.statistical import StatisticalEngineer
        from ml.features.engineers.advanced import AdvancedEngineer
        
        # Создаем feature engineers
        statistical_engineer = StatisticalEngineer(history_size=20)
        advanced_engineer = AdvancedEngineer(history_size=20)
        
        # Имитируем данные, которые будет передавать DataProcessor
        # DataProcessor будет передавать списки чисел из групп
        simulated_dataprocessor_output = [
            [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20],
            [5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 21, 22, 23, 24],
            [9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 21, 22, 23, 24, 1, 2, 3, 4]
        ]
        
        # Проверяем что feature engineers могут обрабатывать данные в формате DataProcessor
        all_features = []
        
        for data_batch in simulated_dataprocessor_output:
            # Statistical features
            stat_features = statistical_engineer.extract_features(data_batch)
            assert stat_features is not None, "Statistical features are None"
            assert isinstance(stat_features, np.ndarray), "Statistical features should be numpy array"
            assert stat_features.dtype == np.float32, "Statistical features should be float32"
            assert stat_features.shape == (50,), f"Statistical features wrong shape: {stat_features.shape}"
            
            # Advanced features (если достаточно данных)
            if len(data_batch) >= 10:
                adv_features = advanced_engineer.extract_features(data_batch)
                assert adv_features is not None, "Advanced features are None"
                assert isinstance(adv_features, np.ndarray), "Advanced features should be numpy array"
                assert adv_features.dtype == np.float32, "Advanced features should be float32"
                assert adv_features.shape == (15,), f"Advanced features wrong shape: {adv_features.shape}"
            
            # Сохраняем для проверки консистентности
            all_features.append(stat_features)
        
        # Проверяем что фичи консистентны между разными батчами
        if len(all_features) > 1:
            # Фичи не должны быть идентичными для разных данных
            first_batch = all_features[0]
            second_batch = all_features[1]
            
            # Они должны быть разными (разные входные данные -> разные фичи)
            assert not np.array_equal(first_batch, second_batch), "Features should be different for different input data"
        
        print("✅ Feature engineers ready for DataProcessor integration")
        print(f"   - Statistical features: {stat_features.shape}")
        print(f"   - Advanced features: {adv_features.shape if len(data_batch) >= 10 else 'N/A'}")
        print(f"   - Processed {len(simulated_dataprocessor_output)} data batches")
        return True
        
    except Exception as e:
        pytest.fail(f"DataProcessor compatibility test failed: {e}")

def test_feature_interface_for_future_integration():
    """Тест интерфейса feature engineers для будущей интеграции"""
    try:
        from ml.features.base import AbstractFeatureEngineer
        from ml.features.engineers.statistical import StatisticalEngineer
        from ml.features.engineers.advanced import AdvancedEngineer
        
        # Проверяем что интерфейс подходит для будущего DataProcessor
        engineers = [
            StatisticalEngineer(history_size=20),
            AdvancedEngineer(history_size=20)
        ]
        
        # DataProcessor будет использовать эти методы:
        required_interface = [
            'extract_features',  # Основной метод для извлечения фич
            'get_feature_names', # Для отладки и логирования
            'history_size',      # Для конфигурации
            'is_fitted'         # Для проверки состояния
        ]
        
        for engineer in engineers:
            for method in required_interface:
                assert hasattr(engineer, method), f"Feature engineer missing {method} for DataProcessor integration"
            
            # Проверяем что extract_features возвращает правильный формат
            test_data = list(range(1, 21))
            features = engineer.extract_features(test_data)
            
            # DataProcessor ожидает numpy array с float32
            assert isinstance(features, np.ndarray), "Features should be numpy array for DataProcessor"
            assert features.dtype == np.float32, "Features should be float32 for DataProcessor"
            assert len(features) > 0, "Features should not be empty for DataProcessor"
        
        print("✅ Feature engineers have correct interface for future DataProcessor")
        return True
        
    except Exception as e:
        pytest.fail(f"Feature interface test failed: {e}")

def test_error_handling_for_dataprocessor_scenarios():
    """Тест обработки ошибок для сценариев DataProcessor"""
    try:
        from ml.features.engineers.statistical import StatisticalEngineer
        from ml.features.engineers.advanced import AdvancedEngineer
        
        statistical_engineer = StatisticalEngineer(history_size=20)
        advanced_engineer = AdvancedEngineer(history_size=20)
        
        # DataProcessor может передавать различные сценарии данных
        test_scenarios = [
            ([], "empty data"),                           # Пустые данные
            ([1, 2, 3], "insufficient data"),            # Недостаточно данных
            (list(range(1, 51)), "large dataset"),       # Большой набор данных
            ([1, 1, 1, 1, 1, 1, 1, 1, 1, 1], "repeated values"),  # Повторяющиеся значения
        ]
        
        for data, scenario_name in test_scenarios:
            # StatisticalEngineer должен обрабатывать все сценарии
            try:
                stat_features = statistical_engineer.extract_features(data)
                assert stat_features is not None, f"StatisticalEngineer failed for {scenario_name}"
                assert stat_features.shape == (50,), f"StatisticalEngineer wrong shape for {scenario_name}"
            except Exception as e:
                pytest.fail(f"StatisticalEngineer should handle {scenario_name}: {e}")
            
            # AdvancedEngineer может требовать больше данных
            if len(data) >= 10:
                try:
                    adv_features = advanced_engineer.extract_features(data)
                    assert adv_features is not None, f"AdvancedEngineer failed for {scenario_name}"
                    assert adv_features.shape == (15,), f"AdvancedEngineer wrong shape for {scenario_name}"
                except Exception as e:
                    pytest.fail(f"AdvancedEngineer should handle {scenario_name}: {e}")
        
        print("✅ Feature engineers handle DataProcessor error scenarios correctly")
        return True
        
    except Exception as e:
        pytest.fail(f"Error handling test failed: {e}")

if __name__ == "__main__":
    test_feature_engineers_ready_for_dataprocessor()
    test_feature_interface_for_future_integration()
    test_error_handling_for_dataprocessor_scenarios()
    print("🎉 Все тесты совместимости с DataProcessor пройдены!")
