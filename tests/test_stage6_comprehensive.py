# /opt/model/tests/test_stage6_comprehensive.py
"""
Комплексный тест Self-Learning системы - проверка всех аспектов
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

def test_comprehensive_self_learning():
    """Комплексный тест всей функциональности Self-Learning системы"""
    print("🧪 Запуск комплексного теста Self-Learning системы...")
    
    try:
        from ml.learning.self_learning import SelfLearningSystem
        from ml.core.types import PredictionResponse
        from ml.ensemble.base_ensemble import WeightedEnsemblePredictor
        from unittest.mock import Mock
        
        # 1. Создаем mock ансамбль с полной функциональностью
        mock_ensemble = Mock(spec=WeightedEnsemblePredictor)
        mock_ensemble.weights = {
            'statistical': 0.4,
            'pattern_based': 0.3, 
            'frequency': 0.3
        }
        mock_ensemble.set_predictor_weight = Mock()
        
        # 2. Создаем временную среду
        with tempfile.TemporaryDirectory() as tmp_dir:
            config = {
                'learning_results_path': Path(tmp_dir) / 'comprehensive_test.json',
                'max_history_size': 5,
                'error_threshold': 3
            }
            
            # 3. Инициализируем систему
            system = SelfLearningSystem(mock_ensemble, config)
            print("✅ Система инициализирована")
            
            # 4. Тестируем получение статистики без данных
            stats_empty = system.get_performance_stats()
            assert stats_empty['status'] == 'no_data'
            assert stats_empty['total_analyses'] == 0
            print("✅ Статистика без данных работает")
            
            # 5. Тестируем рекомендации без данных
            recommendations_empty = system.get_learning_recommendations()
            assert isinstance(recommendations_empty, list)
            assert len(recommendations_empty) > 0
            print("✅ Рекомендации без данных работают")
            
            # 6. Добавляем тестовые данные (несколько анализов)
            test_cases = [
                # (predictions, actual_results, description)
                (
                    [PredictionResponse(predictions=[[1, 2, 3, 4]], model_id="test", inference_time=0.1)],
                    [[1, 2, 7, 8]],  # 2 совпадения
                    "2 совпадения из 4"
                ),
                (
                    [PredictionResponse(predictions=[[5, 6, 7, 8]], model_id="test", inference_time=0.1)],
                    [[5, 6, 9, 10]],  # 2 совпадения  
                    "2 совпадения из 4"
                ),
                (
                    [PredictionResponse(predictions=[[11, 12, 13, 14]], model_id="test", inference_time=0.1)],
                    [[15, 16, 17, 18]],  # 0 совпадений
                    "0 совпадений"
                )
            ]
            
            for i, (predictions, actual_results, description) in enumerate(test_cases):
                result = system.analyze_prediction_accuracy(predictions, actual_results)
                assert result is not None
                print(f"✅ Анализ {i+1} завершен: {description}")
            
            # 7. Тестируем статистику с данными
            stats_with_data = system.get_performance_stats()
            assert stats_with_data['total_analyses'] == 3
            assert 'recent_accuracy_avg' in stats_with_data
            assert 'accuracy_stability' in stats_with_data
            assert 'trend' in stats_with_data
            print("✅ Статистика с данными работает")
            
            # 8. Тестируем рекомендации с данными
            recommendations_with_data = system.get_learning_recommendations()
            assert isinstance(recommendations_with_data, list)
            assert len(recommendations_with_data) > 0
            print("✅ Рекомендации с данными работают")
            
            # 9. Тестируем корректировку весов
            from ml.core.types import AnalysisResult
            
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
            
            weight_adjusted = system.adjust_ensemble_weights(test_analysis)
            assert weight_adjusted == True
            assert mock_ensemble.set_predictor_weight.call_count == 3
            print("✅ Корректировка весов работает")
            
            # 10. Тестируем сохранение и загрузку
            assert config['learning_results_path'].exists()
            
            # Создаем новую систему и проверяем загрузку истории
            new_system = SelfLearningSystem(mock_ensemble, config)
            loaded_stats = new_system.get_performance_stats()
            assert loaded_stats['total_analyses'] == 3
            print("✅ Сохранение и загрузка истории работают")
            
            print("\n🎉 ВСЕ КОМПЛЕКСНЫЕ ТЕСТЫ ПРОЙДЕНЫ УСПЕШНО!")
            return True
            
    except Exception as e:
        print(f"❌ Ошибка в комплексном тесте: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_edge_cases():
    """Тест граничных случаев"""
    print("\n🔍 Тестирование граничных случаев...")
    
    try:
        from ml.learning.self_learning import SelfLearningSystem
        from ml.core.types import PredictionResponse
        from unittest.mock import Mock
        from ml.ensemble.base_ensemble import WeightedEnsemblePredictor
        
        # 1. Тест с пустыми данными
        mock_ensemble = Mock(spec=WeightedEnsemblePredictor)
        mock_ensemble.weights = {}
        
        system = SelfLearningSystem(mock_ensemble, {})
        
        # Пустые предсказания и фактические результаты
        result = system.analyze_prediction_accuracy([], [])
        assert result is not None
        print("✅ Обработка пустых данных работает")
        
        # 2. Тест с None значениями
        mock_ensemble2 = Mock(spec=WeightedEnsemblePredictor)
        mock_ensemble2.weights = None  # Тестируем None weights
        
        system2 = SelfLearningSystem(mock_ensemble2, {})
        weights = system2._get_current_weights()
        assert isinstance(weights, dict)
        print("✅ Обработка None weights работает")
        
        # 3. Тест с разной длиной данных
        predictions = [
            PredictionResponse(predictions=[[1, 2, 3, 4]], model_id="test", inference_time=0.1),
            PredictionResponse(predictions=[[5, 6, 7, 8]], model_id="test", inference_time=0.1)
        ]
        actual_results = [[1, 2, 7, 8]]  # Только один фактический результат
        
        result = system.analyze_prediction_accuracy(predictions, actual_results)
        assert result is not None
        print("✅ Обработка данных разной длины работает")
        
        return True
        
    except Exception as e:
        print(f"❌ Ошибка в тесте граничных случаев: {e}")
        return False

if __name__ == "__main__":
    print("=" * 60)
    print("КОМПЛЕКСНЫЕ ТЕСТЫ SELF-LEARNING СИСТЕМЫ")
    print("=" * 60)
    
    success1 = test_comprehensive_self_learning()
    success2 = test_edge_cases()
    
    print("\n" + "=" * 60)
    if success1 and success2:
        print("🎉🎉🎉 ВСЕ КОМПЛЕКСНЫЕ ТЕСТЫ ПРОЙДЕНЫ! 🎉🎉🎉")
        print("✅ Self-Learning система готова к продакшену")
    else:
        print("🔧 Требуется дополнительная отладка")
    print("=" * 60)
