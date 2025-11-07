# [file name]: test_hurst_fix.py
"""
Тестирование исправления Hurst exponent
"""

import numpy as np
from ml.features.advanced import AdvancedPatternAnalyzer

def test_hurst_calculation():
    """Тестирование расчета Hurst exponent на разных данных"""
    analyzer = AdvancedPatternAnalyzer()
    
    test_cases = [
        ("Нормальные данные", list(range(1, 50))),
        ("Случайные данные", list(np.random.randint(1, 26, 50))),
        ("Постоянные данные", [10] * 50),  # ⚡ ПРОБЛЕМНЫЙ СЛУЧАЙ
        ("Нулевые данные", [0] * 50),      # ⚡ ПРОБЛЕМНЫЙ СЛУЧАЙ  
        ("Отрицательные данные", list(range(-10, 40))),  # ⚡ ПРОБЛЕМНЫЙ СЛУЧАЙ
    ]
    
    print("🧪 ТЕСТИРОВАНИЕ HURST EXPONENT")
    print("=" * 50)
    
    for name, data in test_cases:
        try:
            result = analyzer._calculate_hurst(np.array(data))
            print(f"✅ {name}: Hurst = {result:.3f}")
        except Exception as e:
            print(f"❌ {name}: ОШИБКА - {e}")

if __name__ == "__main__":
    test_hurst_calculation()