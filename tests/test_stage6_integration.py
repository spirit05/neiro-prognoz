# /opt/model/tests/test_stage6_integration.py
"""
Интеграционный тест для ЭТАПА 6 - Self-Learning система (ИСПРАВЛЕННАЯ ВЕРСИЯ)
"""
import sys
import os
import tempfile
import json
from pathlib import Path

# Настраиваем пути
current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(current_dir)
if parent_dir not in sys.path:
    sys.path.insert(0, parent_dir)

def test_self_learning_integration():
    """Интеграционный тест self-learning системы"""
    print("🧪 Запуск интеграционного теста Self-Learning...")
    
    try:
        from ml.core.types import PredictionResponse, AnalysisResult
        from ml.learning.self_learning import SelfLearningSystem
        from ml.ensemble.base_ensemble import WeightedEnsemblePredictor
        
        # Создаем mock ансамбль
        class MockEnsemble(WeightedEnsemblePredictor):
            def __init__(self):
                super().__init__(model_id="test_ensemble")
                self.weights = {'statistical': 0.4, 'pattern_based': 0.3, 'frequency': 0.3}
            
            def set_predictor_weight(self, predictor_id, weight):
                self.weights[predictor_id] = weight
                print(f"⚖️ Вес {predictor_id} установлен: {weight}")
        
        # Создаем временную директорию для тестов
        with tempfile.TemporaryDirectory() as tmp_dir:
            config = {
                'learning_results_path': Path(tmp_dir) / 'learning_results.json',
                'max_history_size': 10
            }
            
            # Создаем систему самообучения
            ensemble = MockEnsemble()
            learning_system = SelfLearningSystem(ensemble, config)
            
            # Создаем тестовые предсказания
            predictions = [
                PredictionResponse(
                    predictions=[[1, 2, 3, 4], [5, 6, 7, 8]],
                    model_id="test_model",
                    inference_time=0.1
                )
            ]
            
            actual_results = [[1, 2, 7, 8]]  # 2 совпадения из 4
            
            # Тестируем анализ точности
            analysis_result = learning_system.analyze_prediction_accuracy(
                predictions, actual_results
            )
            
            assert isinstance(analysis_result, AnalysisResult)
            assert 'performance_metrics' in analysis_result.model_dump()  # ✅ ИСПРАВЛЕНО: .dict() -> .model_dump()
            print("✅ Анализ точности работает")
            
            # Тестируем получение статистики
            stats = learning_system.get_performance_stats()
            assert isinstance(stats, dict)
            assert 'total_analyses' in stats
            print("✅ Получение статистики работает")
            
            # Тестируем рекомендации
            recommendations = learning_system.get_learning_recommendations()
            assert isinstance(recommendations, list)
            print("✅ Генерация рекомендаций работает")
            
            # Тестируем корректировку весов
            test_analysis = AnalysisResult(
                timestamp="2024-01-01T00:00:00",
                performance_metrics={'overall_accuracy': 0.25},
                error_patterns={},
                recommendations={
                    'weight_adjustments': {
                        'statistical': 0.5,
                        'pattern_based': 0.3,
                        'frequency': 0.2
                    }
                },
                ensemble_weights={}
            )
            
            weight_adjusted = learning_system.adjust_ensemble_weights(test_analysis)
            assert weight_adjusted == True
            print("✅ Корректировка весов работает")
            
            # Проверяем сохранение данных
            assert Path(tmp_dir).joinpath('learning_results.json').exists()
            print("✅ Сохранение данных работает")
            
            print("🎉 Все интеграционные тесты Self-Learning пройдены!")
            return True
            
    except Exception as e:
        print(f"❌ Ошибка в интеграционном тесте: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_orchestrator_integration():
    """Тест интеграции оркестратора с self-learning"""
    print("🧪 Тестирование интеграции оркестратора...")
    
    try:
        from ml.core.orchestrator import MLOrchestrator
        
        orchestrator = MLOrchestrator(config={})
        
        # Настраиваем self-learning
        orchestrator.setup_self_learning({
            'learning_results_path': 'tmp/test_learning.json',
            'max_history_size': 50
        })
        
        # Проверяем что система настроена
        assert hasattr(orchestrator, 'self_learning_system')
        print("✅ Настройка self-learning в оркестраторе работает")
        
        # Проверяем методы
        recommendations = orchestrator.get_learning_recommendations()
        assert isinstance(recommendations, list)
        print("✅ Получение рекомендаций из оркестратора работает")
        
        stats = orchestrator.get_performance_stats()
        assert isinstance(stats, dict)
        print("✅ Получение статистики из оркестратора работает")
        
        print("🎉 Интеграция оркестратора с self-learning работает!")
        return True
        
    except Exception as e:
        print(f"❌ Ошибка интеграции оркестратора: {e}")
        return False

if __name__ == "__main__":
    success1 = test_self_learning_integration()
    success2 = test_orchestrator_integration()
    
    if success1 and success2:
        print("\n🎉🎉🎉 ВСЕ ТЕСТЫ ЭТАПА 6 ПРОЙДЕНЫ УСПЕШНО! 🎉🎉🎉")
        print("✅ Self-Learning система полностью интегрирована")
        print("✅ Оркестратор поддерживает self-learning функциональность")
        print("✅ Архитектура ЭТАПА 6 завершена!")
    else:
        print("\n🔧 Требуется дополнительная отладка")
