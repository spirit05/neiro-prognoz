# /opt/model/tests/debug_self_learning.py
"""
Отладочный тест для Self-Learning системы
"""
import sys
import os

# Настраиваем пути
current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(current_dir)
if parent_dir not in sys.path:
    sys.path.insert(0, parent_dir)

def debug_analyze_prediction_accuracy():
    """Отладочный тест метода analyze_prediction_accuracy"""
    from ml.learning.self_learning import SelfLearningSystem
    from ml.core.types import PredictionResponse
    from unittest.mock import Mock
    
    print("🔍 Отладочный тест analyze_prediction_accuracy...")
    
    # Создаем mock ансамбль
    mock_ensemble = Mock()
    mock_ensemble.get_weights.return_value = {'test': 1.0}
    
    # Создаем систему
    system = SelfLearningSystem(mock_ensemble, {})
    
    # Создаем тестовые данные
    predictions = [
        PredictionResponse(
            predictions=[[1, 2, 3, 4]],
            model_id="test_model",
            inference_time=0.1
        )
    ]
    
    actual_results = [[1, 2, 7, 8]]
    
    try:
        print("📊 Вызываем analyze_prediction_accuracy...")
        result = system.analyze_prediction_accuracy(predictions, actual_results)
        print(f"✅ Успех! Результат: {type(result)}")
        print(f"   performance_metrics: {'performance_metrics' in result.model_dump()}")
        print(f"   error_patterns: {'error_patterns' in result.model_dump()}")
        print(f"   recommendations: {'recommendations' in result.model_dump()}")
        return True
    except Exception as e:
        print(f"❌ Ошибка: {e}")
        import traceback
        traceback.print_exc()
        return False

def debug_get_performance_stats():
    """Отладочный тест метода get_performance_stats"""
    from ml.learning.self_learning import SelfLearningSystem
    from unittest.mock import Mock
    
    print("\n🔍 Отладочный тест get_performance_stats...")
    
    # Создаем mock ансамбль
    mock_ensemble = Mock()
    mock_ensemble.get_weights.return_value = {'test': 1.0}
    
    # Создаем систему
    system = SelfLearningSystem(mock_ensemble, {})
    
    try:
        print("📊 Вызываем get_performance_stats без данных...")
        stats_empty = system.get_performance_stats()
        print(f"✅ Успех! Результат: {stats_empty}")
        
        print("📊 Вызываем get_performance_stats с данными...")
        from ml.core.types import PredictionResponse
        
        # Добавляем данные
        predictions = [PredictionResponse(predictions=[[1,2,3,4]], model_id="test", inference_time=0.1)]
        actual_results = [[1,2,7,8]]
        
        system.analyze_prediction_accuracy(predictions, actual_results)
        stats_with_data = system.get_performance_stats()
        print(f"✅ Успех! Результат: {stats_with_data}")
        
        return True
    except Exception as e:
        print(f"❌ Ошибка: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    print("=" * 60)
    print("ОТЛАДОЧНЫЕ ТЕСТЫ SELF-LEARNING СИСТЕМЫ")
    print("=" * 60)
    
    success1 = debug_analyze_prediction_accuracy()
    success2 = debug_get_performance_stats()
    
    print("\n" + "=" * 60)
    if success1 and success2:
        print("🎉 Все отладочные тесты пройдены!")
    else:
        print("🔧 Есть проблемы для исправления")
    print("=" * 60)

