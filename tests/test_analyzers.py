# /opt/model/tests/test_analyzers.py
"""
Тест для проверки работы анализаторов
"""
import sys
import os

# Настраиваем пути
current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(current_dir)
if parent_dir not in sys.path:
    sys.path.insert(0, parent_dir)

def test_analyzers_import():
    """Тест импорта анализаторов"""
    try:
        from ml.learning.analyzers.performance import PerformanceAnalyzer
        from ml.learning.analyzers.error_patterns import ErrorPatternAnalyzer
        
        print("✅ Анализаторы импортируются корректно")
        
        # Проверяем создание экземпляров
        perf_analyzer = PerformanceAnalyzer()
        error_analyzer = ErrorPatternAnalyzer()
        
        assert perf_analyzer is not None
        assert error_analyzer is not None
        
        print("✅ Экземпляры анализаторов создаются корректно")
        assert True
        
    except ImportError as e:
        print(f"❌ Ошибка импорта анализаторов: {e}")
        assert False

def test_analyzers_functionality():
    """Тест функциональности анализаторов"""
    try:
        from ml.learning.analyzers.performance import PerformanceAnalyzer
        from ml.learning.analyzers.error_patterns import ErrorPatternAnalyzer
        from ml.core.types import PredictionResponse
        
        # Создаем тестовые данные
        predictions = [
            PredictionResponse(
                predictions=[[1, 2, 3, 4], [5, 6, 7, 8]],
                model_id="test_model",
                inference_time=0.1
            )
        ]
        
        actual_results = [[1, 2, 7, 8]]  # 2 совпадения
        
        # Тестируем анализатор производительности
        perf_analyzer = PerformanceAnalyzer()
        performance_metrics = perf_analyzer.analyze(predictions, actual_results)
        
        assert 'overall_accuracy' in performance_metrics
        print("✅ Анализатор производительности работает")
        
        # Тестируем анализатор ошибок
        error_analyzer = ErrorPatternAnalyzer()
        error_patterns = error_analyzer.identify_patterns(predictions, actual_results)
        
        assert 'common_errors' in error_patterns
        print("✅ Анализатор ошибок работает")
        
        assert True
        
    except Exception as e:
        print(f"❌ Ошибка функциональности анализаторов: {e}")
        assert False

if __name__ == "__main__":
    print("🧪 Тестирование анализаторов...")
    
    success1 = test_analyzers_import()
    success2 = test_analyzers_functionality()
    
    if success1 and success2:
        print("🎉 Все тесты анализаторов пройдены успешно!")
    else:
        print("🔧 Требуется отладка анализаторов")
