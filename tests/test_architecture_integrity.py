# [file name]: tests/test_architecture_integrity.py
"""
Тест архитектурной целостности новой системы
"""

import pytest
import sys
import os

sys.path.insert(0, '/opt/model')

def test_abstract_feature_engineer_interface():
    """Тест что все feature engineers реализуют правильный интерфейс"""
    try:
        from ml.features.base import AbstractFeatureEngineer
        from ml.features.engineers.statistical import StatisticalEngineer
        from ml.features.engineers.advanced import AdvancedEngineer
        
        # Проверяем наследование
        statistical_engineer = StatisticalEngineer()
        advanced_engineer = AdvancedEngineer()
        
        assert isinstance(statistical_engineer, AbstractFeatureEngineer), "StatisticalEngineer должен наследоваться от AbstractFeatureEngineer"
        assert isinstance(advanced_engineer, AbstractFeatureEngineer), "AdvancedEngineer должен наследоваться от AbstractFeatureEngineer"
        
        # Проверяем наличие обязательных методов
        required_methods = ['extract_features', 'get_feature_names']
        
        for method in required_methods:
            assert hasattr(statistical_engineer, method), f"StatisticalEngineer отсутствует метод {method}"
            assert hasattr(advanced_engineer, method), f"AdvancedEngineer отсутствует метод {method}"
            assert callable(getattr(statistical_engineer, method)), f"StatisticalEngineer.{method} не вызываемый"
            assert callable(getattr(advanced_engineer, method)), f"AdvancedEngineer.{method} не вызываемый"
        
        print("✅ Abstract feature engineer interface test passed")
        return True
        
    except Exception as e:
        pytest.fail(f"Abstract feature engineer interface test failed: {e}")

def test_module_structure():
    """Тест структуры модулей"""
    try:
        # Проверяем что все необходимые модули существуют
        import ml.features
        import ml.features.engineers
        import ml.features.selectors
        import ml.features.transformers
        
        from ml.features import StatisticalEngineer, AdvancedEngineer
        
        # Проверяем что можно создать экземпляры
        statistical_engineer = StatisticalEngineer()
        advanced_engineer = AdvancedEngineer()
        
        assert statistical_engineer is not None, "Cannot create StatisticalEngineer instance"
        assert advanced_engineer is not None, "Cannot create AdvancedEngineer instance"
        
        print("✅ Module structure test passed")
        return True
        
    except Exception as e:
        pytest.fail(f"Module structure test failed: {e}")

if __name__ == "__main__":
    test_abstract_feature_engineer_interface()
    test_module_structure()
    print("🎉 Все тесты архитектурной целостности пройдены!")
