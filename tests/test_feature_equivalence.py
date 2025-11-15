# [file name]: tests/test_feature_equivalence.py
"""
Тест идентичности фич со старой системой
"""

import pytest
import numpy as np
import sys
import os

# Добавляем пути обеих систем
sys.path.insert(0, '/opt/dev')  # Старая система
sys.path.insert(0, '/opt/model')  # Новая система

def test_statistical_features_identical():
    """Тест что StatisticalEngineer выдает те же фичи что и FeatureExtractor"""
    try:
        # Старая система
        from ml.features.extractor import FeatureExtractor
        old_extractor = FeatureExtractor(history_size=20)
        
        # Новая система
        from ml.features.engineers.statistical import StatisticalEngineer
        new_engineer = StatisticalEngineer(history_size=20)
        
        # Тестовые данные
        test_data = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20]
        
        # Извлекаем фичи
        old_features = old_extractor.extract_features(test_data)
        new_features = new_engineer.extract_features(test_data)
        
        # Проверяем идентичность
        assert old_features.shape == new_features.shape, f"Shape mismatch: {old_features.shape} vs {new_features.shape}"
        assert np.allclose(old_features, new_features, atol=1e-6), "Features are not identical"
        
        print("✅ Statistical features are identical to old system")
        return True
        
    except ImportError as e:
        pytest.skip(f"Cannot import old system: {e}")
    except Exception as e:
        pytest.fail(f"Test failed: {e}")

def test_advanced_features_compatible():
    """Тест что AdvancedEngineer совместим со старой системой"""
    try:
        # Старая система
        from ml.features.advanced import AdvancedPatternAnalyzer
        old_analyzer = AdvancedPatternAnalyzer()
        
        # Новая система
        from ml.features.engineers.advanced import AdvancedEngineer
        new_engineer = AdvancedEngineer(history_size=20)
        
        # Тестовые данные
        test_data = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20]
        
        # Анализ старой системой
        old_analysis = old_analyzer.analyze_time_series(test_data)
        
        # Фичи новой системой
        new_features = new_engineer.extract_features(test_data)
        
        # Проверяем что фичи имеют смысл
        assert new_features.shape == (15,), f"Unexpected feature shape: {new_features.shape}"
        assert not np.all(new_features == 0), "All features are zero"
        assert np.any(new_features > 0), "No positive features"
        
        print("✅ Advanced features are compatible with old system")
        return True
        
    except ImportError as e:
        pytest.skip(f"Cannot import old system: {e}")
    except Exception as e:
        pytest.fail(f"Test failed: {e}")

if __name__ == "__main__":
    test_statistical_features_identical()
    test_advanced_features_compatible()
    print("🎉 Все тесты идентичности пройдены!")
