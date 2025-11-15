# [file name]: tests/test_feature_engineers_basic.py
"""
Базовые тесты feature engineers новой системы
"""

import pytest
import numpy as np
import sys
import os

sys.path.insert(0, '/opt/model')

def test_statistical_engineer_functionality():
    """Тест базовой функциональности StatisticalEngineer"""
    try:
        from ml.features.engineers.statistical import StatisticalEngineer
        
        engineer = StatisticalEngineer(history_size=20)
        
        # Тестовые данные
        test_data = list(range(1, 21))  # 20 чисел
        
        # Извлекаем фичи
        features = engineer.extract_features(test_data)
        
        # Проверяем результат
        assert features is not None, "Features are None"
        assert isinstance(features, np.ndarray), f"Features are not numpy array: {type(features)}"
        assert features.dtype == np.float32, f"Wrong dtype: {features.dtype}"
        assert features.shape == (50,), f"Unexpected shape: {features.shape}"
        assert not np.all(features == 0), "All features are zero"
        assert np.any(features > 0), "No positive features"
        
        # Проверяем имена фич
        feature_names = engineer.get_feature_names()
        assert len(feature_names) == 50, f"Unexpected feature names count: {len(feature_names)}"
        assert all(isinstance(name, str) for name in feature_names), "Feature names are not strings"
        
        print(f"✅ StatisticalEngineer: {len(features)} features, {len(feature_names)} names")
        return True
        
    except Exception as e:
        pytest.fail(f"StatisticalEngineer test failed: {e}")

def test_advanced_engineer_functionality():
    """Тест базовой функциональности AdvancedEngineer"""
    try:
        from ml.features.engineers.advanced import AdvancedEngineer
        
        engineer = AdvancedEngineer(history_size=20)
        
        # Тестовые данные
        test_data = list(range(1, 21))  # 20 чисел
        
        # Извлекаем фичи
        features = engineer.extract_features(test_data)
        
        # Проверяем результат
        assert features is not None, "Features are None"
        assert isinstance(features, np.ndarray), f"Features are not numpy array: {type(features)}"
        assert features.dtype == np.float32, f"Wrong dtype: {features.dtype}"
        assert features.shape == (15,), f"Unexpected shape: {features.shape}"
        assert not np.all(features == 0), "All features are zero"
        
        # Проверяем имена фич
        feature_names = engineer.get_feature_names()
        assert len(feature_names) == 15, f"Unexpected feature names count: {len(feature_names)}"
        assert all(isinstance(name, str) for name in feature_names), "Feature names are not strings"
        
        print(f"✅ AdvancedEngineer: {len(features)} features, {len(feature_names)} names")
        return True
        
    except Exception as e:
        pytest.fail(f"AdvancedEngineer test failed: {e}")

def test_edge_cases():
    """Тест обработки крайних случаев"""
    try:
        from ml.features.engineers.statistical import StatisticalEngineer
        from ml.features.engineers.advanced import AdvancedEngineer
        
        statistical_engineer = StatisticalEngineer()
        advanced_engineer = AdvancedEngineer()
        
        # Тест пустых данных
        empty_features_stat = statistical_engineer.extract_features([])
        empty_features_adv = advanced_engineer.extract_features([])
        
        assert np.all(empty_features_stat == 0), "Empty data should return zeros for StatisticalEngineer"
        assert np.all(empty_features_adv == 0), "Empty data should return zeros for AdvancedEngineer"
        
        # Тест недостаточных данных
        small_data = [1, 2, 3]
        small_features_stat = statistical_engineer.extract_features(small_data)
        small_features_adv = advanced_engineer.extract_features(small_data)
        
        assert small_features_stat.shape == (50,), "Small data should still return correct shape for StatisticalEngineer"
        assert small_features_adv.shape == (15,), "Small data should still return correct shape for AdvancedEngineer"
        
        print("✅ Edge cases handled correctly")
        return True
        
    except Exception as e:
        pytest.fail(f"Edge cases test failed: {e}")

if __name__ == "__main__":
    test_statistical_engineer_functionality()
    test_advanced_engineer_functionality() 
    test_edge_cases()
    print("🎉 Все базовые тесты feature engineers пройдены!")
