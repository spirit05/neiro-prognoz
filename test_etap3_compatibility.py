# [file name]: test_etap3_compatibility.py
"""
Тестирование совместимости модулей ЭТАПА 3
"""

import sys
import os

# Добавляем пути новой структуры
sys.path.insert(0, '/opt/dev')

def test_imports():
    """Тестирование всех импортов"""
    print("🧪 ТЕСТИРОВАНИЕ ИМПОРТОВ ЭТАПА 3")
    
    modules_to_test = [
        # Модули самообучения
        ("ml.learning.self_learning", "SelfLearningSystem"),
        
        # Модули ансамбля
        ("ml.ensemble.ensemble", "EnsemblePredictor"),
        ("ml.ensemble.ensemble", "StatisticalPredictor"),
        ("ml.ensemble.ensemble", "PatternBasedPredictor"),
        
        # Продвинутые фичи
        ("ml.features.advanced", "AdvancedPatternAnalyzer"),
        ("ml.features.advanced", "FrequencyBasedPredictor"),
        ("ml.features.advanced", "SmartNumberSelector"),
    ]
    
    success_count = 0
    total_count = len(modules_to_test)
    
    for module_path, class_name in modules_to_test:
        try:
            module = __import__(module_path, fromlist=[class_name])
            class_obj = getattr(module, class_name)
            instance = class_obj()
            print(f"✅ {module_path}.{class_name} - УСПЕХ")
            success_count += 1
        except Exception as e:
            print(f"❌ {module_path}.{class_name} - ОШИБКА: {e}")
    
    print(f"\n📊 РЕЗУЛЬТАТ: {success_count}/{total_count} модулей загружены успешно")
    return success_count == total_count

def test_integration():
    """Тестирование интеграции между модулями"""
    print("\n🔗 ТЕСТИРОВАНИЕ ИНТЕГРАЦИИ")
    
    try:
        # Тест 1: SelfLearningSystem с EnsemblePredictor
        from ml.learning.self_learning import SelfLearningSystem
        from ml.ensemble.ensemble import EnsemblePredictor
        
        learning_system = SelfLearningSystem()
        ensemble = EnsemblePredictor()
        
        # Тест корректировки весов
        result = learning_system.adjust_ensemble_weights(ensemble)
        print(f"✅ SelfLearningSystem + EnsemblePredictor интеграция - УСПЕХ")
        
        # Тест 2: AdvancedPatternAnalyzer
        from ml.features.advanced import AdvancedPatternAnalyzer
        analyzer = AdvancedPatternAnalyzer()
        test_history = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10]
        patterns = analyzer.analyze_time_series(test_history)
        print(f"✅ AdvancedPatternAnalyzer анализ паттернов - УСПЕХ")
        
        # Тест 3: FrequencyBasedPredictor
        from ml.features.advanced import FrequencyBasedPredictor
        freq_predictor = FrequencyBasedPredictor()
        test_dataset = ["1 2 3 4", "5 6 7 8", "1 3 5 7"]
        freq_predictor.update_frequencies(test_dataset)
        score = freq_predictor.get_probability_scores((1, 2, 3, 4))
        print(f"✅ FrequencyBasedPredictor расчет вероятностей - УСПЕХ")
        
        return True
        
    except Exception as e:
        print(f"❌ Ошибка интеграции: {e}")
        return False

def test_functionality():
    """Тестирование функциональности"""
    print("\n⚙️ ТЕСТИРОВАНИЕ ФУНКЦИОНАЛЬНОСТИ")
    
    try:
        # Тест StatisticalPredictor
        from ml.ensemble.ensemble import StatisticalPredictor
        stat_predictor = StatisticalPredictor()
        test_history = list(range(1, 50))  # Создаем тестовую историю
        predictions = stat_predictor.predict(test_history, 5)
        print(f"✅ StatisticalPredictor генерация предсказаний - УСПЕХ ({len(predictions)} прогнозов)")
        
        # Тест PatternBasedPredictor
        from ml.ensemble.ensemble import PatternBasedPredictor
        pattern_predictor = PatternBasedPredictor()
        pattern_predictions = pattern_predictor.predict(test_history, 5)
        print(f"✅ PatternBasedPredictor генерация предсказаний - УСПЕХ ({len(pattern_predictions)} прогнозов)")
        
        # Тест EnsemblePredictor
        from ml.ensemble.ensemble import EnsemblePredictor
        ensemble = EnsemblePredictor()
        ensemble_predictions = ensemble.predict_ensemble(test_history, 10)
        print(f"✅ EnsemblePredictor ансамблевое предсказание - УСПЕХ ({len(ensemble_predictions)} прогнозов)")
        
        # Тест SelfLearningSystem аналитики
        from ml.learning.self_learning import SelfLearningSystem
        learning_system = SelfLearningSystem()
        stats = learning_system.get_performance_stats()
        recommendations = learning_system.get_learning_recommendations()
        print(f"✅ SelfLearningSystem аналитика и рекомендации - УСПЕХ")
        
        return True
        
    except Exception as e:
        print(f"❌ Ошибка функциональности: {e}")
        return False

if __name__ == "__main__":
    print("🚀 ЗАПУСК ТЕСТИРОВАНИЯ ЭТАПА 3")
    print("=" * 50)
    
    # Запускаем все тесты
    import_success = test_imports()
    integration_success = test_integration()
    functionality_success = test_functionality()
    
    print("\n" + "=" * 50)
    print("📊 ИТОГОВЫЕ РЕЗУЛЬТАТЫ ТЕСТИРОВАНИЯ:")
    print(f"✅ Импорты: {'УСПЕХ' if import_success else 'ОШИБКА'}")
    print(f"✅ Интеграция: {'УСПЕХ' if integration_success else 'ОШИБКА'}")
    print(f"✅ Функциональность: {'УСПЕХ' if functionality_success else 'ОШИБКА'}")
    
    if all([import_success, integration_success, functionality_success]):
        print("\n🎉 ВСЕ ТЕСТЫ ПРОЙДЕНЫ! ЭТАП 3 ГОТОВ К РАБОТЕ!")
    else:
        print("\n⚠️  ЕСТЬ ПРОБЛЕМЫ! Нужно исправить ошибки перед продолжением.")