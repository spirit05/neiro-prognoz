# [file name]: tests/test_orchestrator_integration.py
"""
Тест интеграции с оркестратором
"""

import pytest
import sys
import os

sys.path.insert(0, '/opt/model')

def test_orchestrator_feature_registration():
    """Тест регистрации feature engineers в оркестраторе"""
    try:
        from ml.core.orchestrator import MLOrchestrator
        from ml.features.engineers.statistical import StatisticalEngineer
        from ml.features.engineers.advanced import AdvancedEngineer
        
        # Создаем конфигурацию оркестратора
        config = {
            'feature_engineers': {
                'statistical': {
                    'history_size': 20,
                    'enabled': True
                },
                'advanced': {
                    'history_size': 20, 
                    'enabled': True
                }
            }
        }
        
        # Создаем оркестратор
        orchestrator = MLOrchestrator(config)
        
        # Создаем feature engineers
        statistical_engineer = StatisticalEngineer(history_size=20)
        advanced_engineer = AdvancedEngineer(history_size=20)
        
        # Проверяем что engineers могут быть созданы и работают
        test_data = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20]
        
        # Извлекаем фичи
        stat_features = statistical_engineer.extract_features(test_data)
        adv_features = advanced_engineer.extract_features(test_data)
        
        # Проверяем что фичи извлекаются
        assert stat_features is not None, "Statistical features are None"
        assert adv_features is not None, "Advanced features are None"
        assert len(stat_features) > 0, "No statistical features"
        assert len(adv_features) > 0, "No advanced features"
        
        print("✅ Feature engineers work with orchestrator configuration")
        return True
        
    except Exception as e:
        pytest.fail(f"Orchestrator integration test failed: {e}")

def test_feature_engineer_interface():
    """Тест что feature engineers реализуют правильный интерфейс"""
    try:
        from ml.features.base import AbstractFeatureEngineer
        from ml.features.engineers.statistical import StatisticalEngineer
        from ml.features.engineers.advanced import AdvancedEngineer
        
        # Проверяем что engineers наследуются от абстрактного класса
        statistical_engineer = StatisticalEngineer()
        advanced_engineer = AdvancedEngineer()
        
        assert isinstance(statistical_engineer, AbstractFeatureEngineer), "StatisticalEngineer not instance of AbstractFeatureEngineer"
        assert isinstance(advanced_engineer, AbstractFeatureEngineer), "AdvancedEngineer not instance of AbstractFeatureEngineer"
        
        # Проверяем наличие обязательных методов
        assert hasattr(statistical_engineer, 'extract_features'), "StatisticalEngineer missing extract_features"
        assert hasattr(statistical_engineer, 'get_feature_names'), "StatisticalEngineer missing get_feature_names"
        assert hasattr(advanced_engineer, 'extract_features'), "AdvancedEngineer missing extract_features" 
        assert hasattr(advanced_engineer, 'get_feature_names'), "AdvancedEngineer missing get_feature_names"
        
        # Проверяем что методы работают
        test_data = [1, 2, 3, 4, 5]
        
        stat_features = statistical_engineer.extract_features(test_data)
        stat_names = statistical_engineer.get_feature_names()
        
        adv_features = advanced_engineer.extract_features(test_data) 
        adv_names = advanced_engineer.get_feature_names()
        
        assert stat_features is not None, "Statistical features extraction failed"
        assert adv_features is not None, "Advanced features extraction failed"
        assert len(stat_names) > 0, "No statistical feature names"
        assert len(adv_names) > 0, "No advanced feature names"
        
        print("✅ Feature engineer interface test passed")
        return True
        
    except Exception as e:
        pytest.fail(f"Feature engineer interface test failed: {e}")

if __name__ == "__main__":
    test_orchestrator_feature_registration()
    test_feature_engineer_interface()
    print("🎉 Все тесты интеграции с оркестратором пройдены!")
