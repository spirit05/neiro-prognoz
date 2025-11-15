# [file name]: tests/test_future_compatibility.py
"""
Тест готовности feature engineers к будущей интеграции
ЗАМЕНА test_dataprocessor_integration.py - не требует DataProcessor
"""

import pytest
import numpy as np
import sys
import os

sys.path.insert(0, '/opt/model')

def test_feature_engineers_produce_consistent_output():
    """Тест что feature engineers выдают консистентный выходной формат"""
    try:
        from ml.features.engineers.statistical import StatisticalEngineer
        from ml.features.engineers.advanced import AdvancedEngineer
        
        # Создаем инженеров
        statistical_engineer = StatisticalEngineer(history_size=20)
        advanced_engineer = AdvancedEngineer(history_size=20)
        
        # Тестовые данные (имитация того, что будет передавать будущий DataProcessor)
        test_data_sets = [
            list(range(1, 21)),  # 20 чисел
            list(range(5, 25)),  # другой набор
            [1, 3, 5, 7, 9, 11, 13, 15, 17, 19, 21, 23, 25, 2, 4, 6, 8, 10, 12, 14]  # перемешанные
        ]
        
        for i, test_data in enumerate(test_data_sets):
            print(f"Testing dataset {i+1}: {len(test_data)} numbers")
            
            # StatisticalEngineer тест
            stat_features = statistical_engineer.extract_features(test_data)
            assert stat_features is not None, f"Statistical features None for dataset {i+1}"
            assert isinstance(stat_features, np.ndarray), f"Statistical features not numpy array for dataset {i+1}"
            assert stat_features.dtype == np.float32, f"Statistical features wrong dtype for dataset {i+1}"
            assert stat_features.shape == (50,), f"Statistical features wrong shape for dataset {i+1}"
            
            # AdvancedEngineer тест (только если достаточно данных)
            if len(test_data) >= 10:
                adv_features = advanced_engineer.extract_features(test_data)
                assert adv_features is not None, f"Advanced features None for dataset {i+1}"
                assert isinstance(adv_features, np.ndarray), f"Advanced features not numpy array for dataset {i+1}"
                assert adv_features.dtype == np.float32, f"Advanced features wrong dtype for dataset {i+1}"
                assert adv_features.shape == (15,), f"Advanced features wrong shape for dataset {i+1}"
        
        print("✅ Feature engineers produce consistent output format")
        return True
        
    except Exception as e:
        pytest.fail(f"Feature output consistency test failed: {e}")

def test_ready_for_future_integration():
    """Тест что feature engineers готовы к будущей интеграции"""
    try:
        from ml.features.engineers.statistical import StatisticalEngineer
        from ml.features.engineers.advanced import AdvancedEngineer
        
        # Проверяем что у нас есть все необходимое для будущей интеграции
        engineers = {
            'statistical': StatisticalEngineer(),
            'advanced': AdvancedEngineer()
        }
        
        # Критерии готовности для будущего DataProcessor
        readiness_criteria = [
            ('has extract_features method', lambda e: hasattr(e, 'extract_features') and callable(e.extract_features)),
            ('has get_feature_names method', lambda e: hasattr(e, 'get_feature_names') and callable(e.get_feature_names)),
            ('returns numpy arrays', lambda e: isinstance(e.extract_features([1,2,3,4,5]), np.ndarray)),
            ('returns correct dtypes', lambda e: e.extract_features([1,2,3,4,5]).dtype == np.float32),
            ('configurable history_size', lambda e: hasattr(e, 'history_size')),
        ]
        
        for engineer_name, engineer in engineers.items():
            print(f"Checking {engineer_name}...")
            for criterion_name, criterion_check in readiness_criteria:
                assert criterion_check(engineer), f"{engineer_name} failed: {criterion_name}"
                print(f"  ✅ {criterion_name}")
        
        print("✅ All feature engineers ready for future integration")
        return True
        
    except Exception as e:
        pytest.fail(f"Future integration readiness test failed: {e}")

if __name__ == "__main__":
    test_feature_engineers_produce_consistent_output()
    test_ready_for_future_integration()
    print("🎉 Все тесты будущей совместимости пройдены!")
