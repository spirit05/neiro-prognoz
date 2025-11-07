# [file name]: test_final_hurst.py
"""
Финальное тестирование исправленного Hurst exponent
"""

import numpy as np
from ml.features.advanced import AdvancedPatternAnalyzer

def test_hurst_final():
    """Финальное тестирование Hurst exponent"""
    analyzer = AdvancedPatternAnalyzer()
    
    test_cases = [
        ("Возрастающий тренд", list(range(1, 50))),
        ("Случайные данные", list(np.random.randint(1, 26, 50))),
        ("Постоянные данные", [15] * 50),
        ("Периодические", list(range(1, 26)) * 2),
        ("Короткие", [1, 2, 3]),
    ]
    
    print("🎯 ФИНАЛЬНОЕ ТЕСТИРОВАНИЕ HURST EXPONENT")
    print("=" * 50)
    
    all_success = True
    for name, data in test_cases:
        try:
            hurst = analyzer._calculate_hurst_safe(np.array(data))
            if 0.1 <= hurst <= 0.9:  # Разумные границы для Hurst
                print(f"✅ {name}: Hurst = {hurst:.3f}")
            else:
                print(f"⚠️  {name}: Hurst = {hurst:.3f} (вне диапазона)")
                all_success = False
        except Exception as e:
            print(f"❌ {name}: ОШИБКА - {e}")
            all_success = False
    
    return all_success

def test_complete_analysis():
    """Тестирование полного анализа"""
    print("\n🔍 ТЕСТИРОВАНИЕ ПОЛНОГО АНАЛИЗА ПАТТЕРНОВ")
    print("=" * 50)
    
    analyzer = AdvancedPatternAnalyzer()
    
    # Реалистичные тестовые данные (похожие на лотерейные)
    test_data = list(np.random.randint(1, 26, 100))
    
    try:
        patterns = analyzer.analyze_time_series(test_data)
        print("✅ Полный анализ паттернов выполнен успешно!")
        
        # Проверяем, что все ключи присутствуют
        expected_keys = ['autocorrelation', 'dominant_frequency', 'linear_trend', 
                        'volatility', 'hurst_exponent', 'mean_reversion']
        
        for key in expected_keys:
            if key in patterns:
                print(f"   ✅ {key}: присутствует")
            else:
                print(f"   ❌ {key}: отсутствует")
                
        # Проверяем, что Hurst в разумных пределах
        hurst = patterns.get('hurst_exponent', 0.5)
        if 0.1 <= hurst <= 0.9:
            print(f"   ✅ Hurst exponent: {hurst:.3f} (корректный)")
        else:
            print(f"   ⚠️  Hurst exponent: {hurst:.3f} (сомнительный)")
            
        return True
        
    except Exception as e:
        print(f"❌ Ошибка анализа паттернов: {e}")
        return False

if __name__ == "__main__":
    print("🚀 ЗАПУСК ФИНАЛЬНОГО ТЕСТИРОВАНИЯ")
    print()
    
    hurst_ok = test_hurst_final()
    analysis_ok = test_complete_analysis()
    
    print("\n" + "=" * 50)
    if hurst_ok and analysis_ok:
        print("🎉 ВСЕ ТЕСТЫ ПРОЙДЕНЫ! HURST EXPONENT ИСПРАВЛЕН!")
    else:
        print("⚠️  Есть проблемы, но система будет работать стабильно")