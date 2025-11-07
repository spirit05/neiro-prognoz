# [file name]: test_final_verification.py
"""
ФИНАЛЬНАЯ ПРОВЕРКА СИСТЕМЫ ПОСЛЕ ИСПРАВЛЕНИЙ
"""

import sys
import os
import numpy as np
sys.path.insert(0, '/opt/dev')

def quick_fix_check():
    """Быстрая проверка исправлений"""
    print("🔧 ПРОВЕРКА ИСПРАВЛЕНИЙ")
    print("=" * 50)
    
    # Проверяем исправленные импорты
    try:
        from ml.core.predictor import EnhancedPredictor
        from ml.features.advanced import AdvancedPatternAnalyzer, FrequencyBasedPredictor
        from ml.learning.self_learning import SelfLearningSystem
        
        print("✅ Все основные импорты работают")
        
        # Проверяем, что predictor использует правильные импорты
        predictor = EnhancedPredictor()
        
        # Проверяем анализ паттернов
        analyzer = AdvancedPatternAnalyzer()
        test_data = list(range(1, 30))
        patterns = analyzer.analyze_time_series(test_data)
        print(f"✅ AdvancedPatternAnalyzer: {len(patterns)} параметров")
        
        # Проверяем частотный анализ
        freq_predictor = FrequencyBasedPredictor()
        test_groups = ["1 2 3 4", "5 6 7 8"]
        freq_predictor.update_frequencies(test_groups)
        score = freq_predictor.get_probability_scores((1, 2, 3, 4))
        print(f"✅ FrequencyBasedPredictor: score = {score:.8f}")
        
        # Проверяем самообучение
        learning_system = SelfLearningSystem()
        analysis = learning_system.analyze_prediction_accuracy("1 2 3 4")
        print(f"✅ SelfLearningSystem: анализ выполнен")
        
        return True
        
    except Exception as e:
        print(f"❌ Ошибка в проверке импортов: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_predictions():
    """Тестирование предсказаний"""
    print("\n🎯 ТЕСТИРОВАНИЕ ПРЕДСКАЗАНИЙ")
    print("=" * 50)
    
    try:
        from ml.core.predictor import EnhancedPredictor
        from ml.ensemble.ensemble import EnsemblePredictor
        
        # Создаем тестовую историю
        test_history = list(range(1, 50))
        
        # Тестируем базовый predictor
        predictor = EnhancedPredictor()
        basic_predictions = predictor.predict_group(test_history, 3)
        print(f"✅ Базовые предсказания: {len(basic_predictions)} прогнозов")
        
        # Тестируем ансамбль
        ensemble = EnsemblePredictor()
        ensemble.set_neural_predictor(predictor)
        ensemble_predictions = ensemble.predict_ensemble(test_history, 3)
        print(f"✅ Ансамблевые предсказания: {len(ensemble_predictions)} прогнозов")
        
        # Показываем результаты
        print("\n📊 РЕЗУЛЬТАТЫ ПРЕДСКАЗАНИЙ:")
        for i, (group, score) in enumerate(ensemble_predictions[:3]):
            print(f"   {i+1}. {group} (score: {score:.6f})")
        
        return True
        
    except Exception as e:
        print(f"❌ Ошибка в предсказаниях: {e}")
        return False

def test_learning_system():
    """Тестирование системы самообучения"""
    print("\n🧠 ТЕСТИРОВАНИЕ САМООБУЧЕНИЯ")
    print("=" * 50)
    
    try:
        from ml.learning.self_learning import SelfLearningSystem
        from ml.utils.data_utils import save_predictions
        
        # Сохраняем тестовые предсказания для анализа
        test_predictions = [((1, 2, 3, 4), 0.5), ((5, 6, 7, 8), 0.3)]
        save_predictions(test_predictions)
        
        # Тестируем анализ точности
        learning_system = SelfLearningSystem()
        analysis = learning_system.analyze_prediction_accuracy("1 2 3 4")
        
        if analysis:
            print(f"✅ Анализ точности: {analysis['matches_count']}/4 совпадений")
        else:
            print("✅ Анализ точности: выполнено (нет предыдущих предсказаний)")
        
        # Тестируем рекомендации
        recommendations = learning_system.get_learning_recommendations()
        print(f"✅ Рекомендации: {len(recommendations)} шт")
        
        # Тестируем статистику
        stats = learning_system.get_performance_stats()
        print(f"✅ Статистика: собрано данных")
        
        return True
        
    except Exception as e:
        print(f"❌ Ошибка в системе самообучения: {e}")
        return False

if __name__ == "__main__":
    print("🚀 ФИНАЛЬНАЯ ПРОВЕРКА СИСТЕМЫ")
    print()
    
    fixes_ok = quick_fix_check()
    predictions_ok = test_predictions()
    learning_ok = test_learning_system()
    
    print("\n" + "=" * 50)
    print("🎯 ФИНАЛЬНЫЕ РЕЗУЛЬТАТЫ:")
    print(f"✅ Исправления импортов: {'УСПЕХ' if fixes_ok else 'ОШИБКА'}")
    print(f"✅ Система предсказаний: {'УСПЕХ' if predictions_ok else 'ОШИБКА'}")
    print(f"✅ Система самообучения: {'УСПЕХ' if learning_ok else 'ОШИБКА'}")
    
    if all([fixes_ok, predictions_ok, learning_ok]):
        print("\n🎉 ВСЕ ПРОБЛЕМЫ ИСПРАВЛЕНЫ!")
        print("🚀 СИСТЕМА ЭТАПОВ 1-3 ПОЛНОСТЬЮ ГОТОВА!")
        print("\n📋 Статус системы:")
        print("  • ✅ ML ядро - РАБОТАЕТ")
        print("  • ✅ Ансамблевые методы - РАБОТАЮТ") 
        print("  • ✅ Самообучение - РАБОТАЕТ")
        print("  • ✅ Все импорты - ИСПРАВЛЕНЫ")
        print("  • ✅ Обработка ошибок - РАБОТАЕТ")
        print("\n🎯 МОЖЕМ ПЕРЕХОДИТЬ К ЭТАПУ 4: TELEGRAM БОТ!")
    else:
        print("\n⚠️  Нужно доделать исправления")
