# [file name]: test_hurst_fix_v2.py
"""
Тестирование исправленного Hurst exponent
"""

import numpy as np
from ml.features.advanced import AdvancedPatternAnalyzer

def test_hurst_calculation():
    """Тестирование расчета Hurst exponent на разных данных"""
    analyzer = AdvancedPatternAnalyzer()
    
    test_cases = [
        ("Нормальные данные", list(range(1, 50))),
        ("Случайные данные", list(np.random.randint(1, 26, 50))),
        ("Постоянные данные", [10] * 50),
        ("Нулевые данные", [0] * 50),  
        ("Отрицательные данные", list(range(-10, 40))),
        ("С пропусками", [1, 2, 3] + [0] * 10 + [4, 5, 6]),
        ("Короткие данные", [1, 2, 3]),  # Слишком короткие
    ]
    
    print("🧪 ТЕСТИРОВАНИЕ ИСПРАВЛЕННОГО HURST EXPONENT")
    print("=" * 60)
    
    for name, data in test_cases:
        try:
            result = analyzer._calculate_hurst(np.array(data))
            status = "✅" if 0 <= result <= 2 else "⚠️"
            print(f"{status} {name}: Hurst = {result:.3f}")
        except Exception as e:
            print(f"❌ {name}: ОШИБКА - {e}")

def test_pattern_analyzer_complete():
    """Тестирование полного анализа паттернов"""
    print("\n🔍 ТЕСТИРОВАНИЕ ПОЛНОГО АНАЛИЗА ПАТТЕРНОВ")
    print("=" * 50)
    
    analyzer = AdvancedPatternAnalyzer()
    
    # Тестовые данные
    test_data = list(range(1, 30)) + list(range(15, 25))
    
    try:
        patterns = analyzer.analyze_time_series(test_data)
        print("✅ Полный анализ паттернов выполнен успешно!")
        print(f"📊 Найдено паттернов: {len(patterns)}")
        
        for key, value in patterns.items():
            if isinstance(value, dict):
                print(f"   {key}: {len(value)} параметров")
            else:
                print(f"   {key}: {value}")
                
    except Exception as e:
        print(f"❌ Ошибка анализа паттернов: {e}")

if __name__ == "__main__":
    test_hurst_calculation()
    test_pattern_analyzer_complete()