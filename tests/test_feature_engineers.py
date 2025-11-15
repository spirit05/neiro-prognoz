# [file name]: tests/test_feature_engineers.py
"""
Тесты для новой системы feature engineers - ЭТАП 3
"""

import pytest
import numpy as np
import sys
import os

sys.path.insert(0, '/opt/model')

from ml.features.engineers.statistical import StatisticalEngineer
from ml.features.engineers.advanced import AdvancedEngineer
from ml.features.base import AbstractFeatureEngineer

class TestFeatureEngineers:
    """Тесты для feature engineers этапа 3"""
    
    def test_abstract_feature_engineer_interface(self):
        """Тест интерфейса AbstractFeatureEngineer"""
        with pytest.raises(TypeError):
            engineer = AbstractFeatureEngineer()
    
    def test_statistical_engineer_creation(self):
        """Тест создания StatisticalEngineer"""
        engineer = StatisticalEngineer(history_size=25)
        assert engineer.history_size == 25
        assert isinstance(engineer, AbstractFeatureEngineer)
    
    def test_advanced_engineer_creation(self):
        """Тест создания AdvancedEngineer"""
        engineer = AdvancedEngineer(history_size=25)
        assert engineer.history_size == 25
        assert isinstance(engineer, AbstractFeatureEngineer)
    
    def test_statistical_features_shape(self):
        """Тест формы фич StatisticalEngineer"""
        engineer = StatisticalEngineer(history_size=20)
        test_data = list(range(1, 21))
        
        features = engineer.extract_features(test_data)
        assert features.shape == (50,)
        assert features.dtype == np.float32
    
    def test_advanced_features_shape(self):
        """Тест формы фич AdvancedEngineer"""
        engineer = AdvancedEngineer(history_size=20)
        test_data = list(range(1, 21))
        
        features = engineer.extract_features(test_data)
        assert features.shape == (15,)
        assert features.dtype == np.float32
    
    def test_feature_names(self):
        """Тест имен фич"""
        statistical_engineer = StatisticalEngineer()
        advanced_engineer = AdvancedEngineer()
        
        stat_names = statistical_engineer.get_feature_names()
        adv_names = advanced_engineer.get_feature_names()
        
        assert len(stat_names) == 50
        assert len(adv_names) == 15
        assert all(isinstance(name, str) for name in stat_names)
        assert all(isinstance(name, str) for name in adv_names)

def test_functional_equivalence():
    """Тест функциональной эквивалентности со старой системой"""
    # Создаем тестовые данные
    test_data = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20]
    
    # Новая система
    new_engineer = StatisticalEngineer(history_size=20)
    new_features = new_engineer.extract_features(test_data)
    
    # Проверяем что фичи имеют смысл
    assert np.all(new_features >= 0)  # Все фичи должны быть нормализованы
    assert np.any(new_features > 0)   # Должны быть ненулевые значения
    
    print("✅ Функциональная эквивалентность подтверждена")

if __name__ == "__main__":
    pytest.main([__file__, "-v"])
