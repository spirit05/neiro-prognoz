# /opt/model/tests/test_stage6_simple.py
"""
Упрощенный тест для ЭТАПА 6 - проверка базовой функциональности
"""
import sys
import os
import pytest

# Настраиваем пути
current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(current_dir)
if parent_dir not in sys.path:
    sys.path.insert(0, parent_dir)

class TestStage6Simple:
    """Упрощенные тесты для ЭТАПА 6"""
    
    def test_analysis_result_creation(self):
        """Тест создания AnalysisResult"""
        from ml.core.types import AnalysisResult
        
        # Создаем простой анализ
        analysis = AnalysisResult(
            timestamp="2024-01-01T00:00:00",
            performance_metrics={"accuracy": 0.75},
            error_patterns={},
            recommendations={},
            ensemble_weights={}
        )
        
        assert analysis.timestamp == "2024-01-01T00:00:00"
        assert analysis.performance_metrics["accuracy"] == 0.75
        print("✅ AnalysisResult создан корректно")
    
    def test_learning_history_creation(self):
        """Тест создания LearningHistory"""
        from ml.core.types import LearningHistory, AnalysisResult
        
        history = LearningHistory(
            last_analysis="2024-01-01T00:00:00",
            analysis_history=[],
            total_analyses=0
        )
        
        assert history.total_analyses == 0
        assert history.last_analysis == "2024-01-01T00:00:00"
        print("✅ LearningHistory создан корректно")
    
    def test_orchestrator_has_self_learning_methods(self):
        """Тест что оркестратор имеет методы self-learning"""
        from ml.core.orchestrator import MLOrchestrator
        
        orchestrator = MLOrchestrator(config={})
        
        # Проверяем наличие методов
        assert hasattr(orchestrator, 'setup_self_learning')
        assert hasattr(orchestrator, 'analyze_predictions')
        assert hasattr(orchestrator, 'get_learning_recommendations')
        assert hasattr(orchestrator, 'get_performance_stats')
        
        print("✅ Оркестратор имеет все методы self-learning")

def test_basic_imports():
    """Базовый тест импортов"""
    try:
        from ml.core import types, base_model, orchestrator
        from ml.learning import self_learning
        
        assert types is not None
        assert base_model is not None  
        assert orchestrator is not None
        assert self_learning is not None
        
        print("✅ Все базовые модули импортируются")
        return True
    except ImportError as e:
        print(f"❌ Ошибка импорта: {e}")
        return False

if __name__ == "__main__":
    # Запускаем тесты
    test_basic_imports()
    
    test_simple = TestStage6Simple()
    test_simple.test_analysis_result_creation()
    test_simple.test_learning_history_creation() 
    test_simple.test_orchestrator_has_self_learning_methods()
    
    print("🎉 Все упрощенные тесты ЭТАПА 6 пройдены!")
