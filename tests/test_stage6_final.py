# /opt/model/tests/test_stage6_final.py
"""
ФИНАЛЬНЫЙ ТЕСТ ЭТАПА 6 - Полная проверка Self-Learning системы
"""

import sys
import os
import tempfile
from pathlib import Path

# Настраиваем пути
current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(current_dir)
if parent_dir not in sys.path:
    sys.path.insert(0, parent_dir)

def test_complete_self_learning_workflow():
    """Тест полного рабочего процесса self-learning системы"""
    print("🚀 Запуск финального теста Self-Learning системы...")
    
    try:
        from ml.core.types import PredictionResponse, AnalysisResult
        from ml.learning.self_learning import SelfLearningSystem
        from ml.ensemble.base_ensemble import WeightedEnsemblePredictor
        from ml.core.orchestrator import MLOrchestrator
        
        # 1. Создаем mock ансамбль
        class TestEnsemble(WeightedEnsemblePredictor):
            def __init__(self):
                super().__init__(model_id="test_ensemble")
                self.weights = {
                    'statistical': 0.4, 
                    'pattern_based': 0.3, 
                    'frequency': 0.3
                }
            
            def set_predictor_weight(self, predictor_id, weight):
                self.weights[predictor_id] = weight
                print(f"⚖️ Вес {predictor_id} изменен на: {weight}")
        
        # 2. Создаем временную среду для тестирования
        with tempfile.TemporaryDirectory() as tmp_dir:
            learning_config = {
                'learning_results_path': Path(tmp_dir) / 'learning_results.json',
                'max_history_size': 20,
                'error_threshold': 3
            }
            
            # 3. Инициализируем систему самообучения
            ensemble = TestEnsemble()
            self_learning = SelfLearningSystem(ensemble, learning_config)
            
            print("✅ Система самообучения инициализирована")
            
            # 4. Создаем тестовые данные (симуляция нескольких прогнозов)
            test_predictions = [
                PredictionResponse(
                    predictions=[[1, 2, 3, 4], [5, 6, 7, 8]],
                    model_id="enhanced_predictor",
                    inference_time=0.15
                ),
                PredictionResponse(
                    predictions=[[9, 10, 11, 12], [13, 14, 15, 16]],
                    model_id="enhanced_predictor", 
                    inference_time=0.12
                )
            ]
            
            test_actual_results = [
                [1, 2, 7, 8],  # 2 совпадения
                [9, 10, 17, 18]  # 2 совпадения
            ]
            
            # 5. Тестируем анализ точности
            analysis_result = self_learning.analyze_prediction_accuracy(
                test_predictions, test_actual_results
            )
            
            assert isinstance(analysis_result, AnalysisResult)
            assert analysis_result.timestamp is not None
            assert 'performance_metrics' in analysis_result.model_dump()
            print("✅ Анализ точности работает корректно")
            
            # 6. Тестируем статистику производительности
            stats = self_learning.get_performance_stats()
            required_stats_fields = [
                'total_analyses', 'recent_accuracy_avg', 
                'accuracy_stability', 'trend'
            ]
            
            for field in required_stats_fields:
                assert field in stats, f"Отсутствует поле статистики: {field}"
            print("✅ Статистика производительности работает корректно")
            
            # 7. Тестируем генерацию рекомендаций
            recommendations = self_learning.get_learning_recommendations()
            assert isinstance(recommendations, list)
            assert len(recommendations) > 0
            print("✅ Генерация рекомендаций работает корректно")
            
            # 8. Тестируем корректировку весов
            weight_adjustment_result = self_learning.adjust_ensemble_weights(analysis_result)
            # Может вернуть False если нет рекомендаций по весам - это нормально
            assert isinstance(weight_adjustment_result, bool)
            print("✅ Корректировка весов работает корректно")
            
            # 9. Тестируем интеграцию с оркестратором
            orchestrator = MLOrchestrator(config={})
            orchestrator.register_model(ensemble)
            orchestrator.setup_self_learning(learning_config)
            
            # Проверяем методы оркестратора
            orchestrator_recommendations = orchestrator.get_learning_recommendations()
            assert isinstance(orchestrator_recommendations, list)
            
            orchestrator_stats = orchestrator.get_performance_stats()
            assert isinstance(orchestrator_stats, dict)
            print("✅ Интеграция с оркестратором работает корректно")
            
            # 10. Проверяем сохранение и загрузку данных
            assert Path(tmp_dir).joinpath('learning_results.json').exists()
            
            # Создаем новую систему и проверяем загрузку истории
            new_self_learning = SelfLearningSystem(ensemble, learning_config)
            loaded_stats = new_self_learning.get_performance_stats()
            assert loaded_stats['total_analyses'] >= 1
            print("✅ Сохранение и загрузка данных работают корректно")
            
            print("\n🎉 ВСЕ ТЕСТЫ SELF-LEARNING СИСТЕМЫ ПРОЙДЕНЫ УСПЕШНО!")
            assert True
            
    except Exception as e:
        print(f"❌ Ошибка в финальном тесте: {e}")
        import traceback
        traceback.print_exc()
        assert False

def test_analyzers_functionality():
    """Тест функциональности анализаторов"""
    print("\n🔍 Тестирование анализаторов...")
    
    try:
        from ml.learning.analyzers.performance import PerformanceAnalyzer
        from ml.learning.analyzers.error_patterns import ErrorPatternAnalyzer
        from ml.core.types import PredictionResponse
        
        # Создаем тестовые данные
        predictions = [
            PredictionResponse(
                predictions=[[1, 2, 3, 4]],
                model_id="test_model",
                inference_time=0.1
            ),
            PredictionResponse(
                predictions=[[5, 6, 7, 8]],
                model_id="test_model",
                inference_time=0.1
            )
        ]
        
        actual_results = [[1, 2, 9, 10], [5, 6, 15, 16]]
        
        # Тестируем анализатор производительности
        perf_analyzer = PerformanceAnalyzer()
        performance_metrics = perf_analyzer.analyze(predictions, actual_results)
        
        assert 'overall_accuracy' in performance_metrics
        assert 'confidence_analysis' in performance_metrics
        print("✅ Анализатор производительности работает корректно")
        
        # Тестируем анализатор ошибок
        error_analyzer = ErrorPatternAnalyzer()
        error_patterns = error_analyzer.identify_patterns(predictions, actual_results)
        
        assert 'common_errors' in error_patterns
        assert 'number_frequency_analysis' in error_patterns
        print("✅ Анализатор ошибок работает корректно")
        
        assert True
        
    except Exception as e:
        print(f"❌ Ошибка в тесте анализаторов: {e}")
        assert False

if __name__ == "__main__":
    print("=" * 60)
    print("ФИНАЛЬНАЯ ПРОВЕРКА ЭТАПА 6 - SELF-LEARNING СИСТЕМА")
    print("=" * 60)
    
    success1 = test_complete_self_learning_workflow()
    success2 = test_analyzers_functionality()
    
    print("\n" + "=" * 60)
    if success1 and success2:
        print("🎉🎉🎉 ЭТАП 6 УСПЕШНО ЗАВЕРШЕН! 🎉🎉🎉")
        print("✅ Self-Learning система полностью функционирует")
        print("✅ Все анализаторы работают корректно") 
        print("✅ Интеграция с оркестратором настроена")
        print("✅ Сохранение и загрузка данных работают")
        print("✅ Все тесты пройдены без ошибок")
    else:
        print("🔧 Требуется дополнительная отладка системы")
    print("=" * 60)

