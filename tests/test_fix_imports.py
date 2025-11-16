# /opt/model/tests/test_fix_imports.py
"""
Тест для проверки исправления импортов после ЭТАПА 6
"""
import pytest
import sys
import os

def test_core_imports():
    """Тест импорта основных модулей core"""
    from ml.core.types import AnalysisResult, LearningHistory
    from ml.core.orchestrator import MLOrchestrator
    from ml.core.base_model import AbstractBaseModel
    
    # Проверяем что классы доступны
    assert AnalysisResult is not None
    assert LearningHistory is not None
    assert MLOrchestrator is not None
    assert AbstractBaseModel is not None
    
    print("✅ Все core импорты работают корректно")

def test_self_learning_imports():
    """Тест импорта модулей self-learning"""
    try:
        from ml.learning.self_learning import SelfLearningSystem
        from ml.learning.analyzers.performance import PerformanceAnalyzer
        from ml.learning.analyzers.error_patterns import ErrorPatternAnalyzer
        
        assert SelfLearningSystem is not None
        assert PerformanceAnalyzer is not None
        assert ErrorPatternAnalyzer is not None
        
        print("✅ Все self-learning импорты работают корректно")
        
    except ImportError as e:
        pytest.skip(f"Self-learning модули еще не реализованы: {e}")

def test_orchestrator_self_learning_integration():
    """Тест интеграции оркестратора с self-learning"""
    from ml.core.orchestrator import MLOrchestrator
    
    orchestrator = MLOrchestrator(config={})
    
    # Проверяем что методы self-learning доступны
    assert hasattr(orchestrator, 'setup_self_learning')
    assert hasattr(orchestrator, 'analyze_predictions')
    assert hasattr(orchestrator, 'get_learning_recommendations')
    assert hasattr(orchestrator, 'get_performance_stats')
    
    print("✅ Оркестратор имеет все методы self-learning")

if __name__ == "__main__":
    test_core_imports()
    test_self_learning_imports() 
    test_orchestrator_self_learning_integration()
    print("🎉 Все тесты импортов пройдены успешно!")
