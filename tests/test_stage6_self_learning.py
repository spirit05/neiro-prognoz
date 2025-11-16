# /opt/model/tests/test_stage6_self_learning.py
import pytest
import tempfile
import json
from pathlib import Path
from unittest.mock import Mock

from ml.learning.self_learning import SelfLearningSystem
from ml.learning.analyzers.performance import PerformanceAnalyzer
from ml.learning.analyzers.error_patterns import ErrorPatternAnalyzer
from ml.core.types import PredictionResponse, AnalysisResult
from ml.ensemble.base_ensemble import WeightedEnsemblePredictor


class TestSelfLearningSystem:
    
    def setup_method(self):
        """Настройка тестов"""
        self.mock_ensemble = Mock(spec=WeightedEnsemblePredictor)
        self.mock_ensemble.weights = {
            'statistical': 0.4,
            'pattern_based': 0.3,
            'frequency': 0.3
        }
        
        self.config = {
            'learning_results_path': 'tmp/test_learning_results.json',
            'max_history_size': 10
        }
        
        with tempfile.TemporaryDirectory() as tmp_dir:
            self.learning_system = SelfLearningSystem(
                self.mock_ensemble, 
                {**self.config, 'learning_results_path': Path(tmp_dir) / 'learning_results.json'}
            )

    def test_initialization(self):
        """Тест инициализации системы самообучения"""
        assert self.learning_system.ensemble == self.mock_ensemble
        assert self.learning_system.config['max_history_size'] == 10
        assert isinstance(self.learning_system.performance_analyzer, PerformanceAnalyzer)
        assert isinstance(self.learning_system.error_analyzer, ErrorPatternAnalyzer)

    def test_analyze_prediction_accuracy(self):
        """Тест анализа точности предсказаний"""
        # Создаем тестовые предсказания
        predictions = [
            PredictionResponse(
                predictions=[[1, 2, 3, 4]],
                probabilities=[[0.9, 0.8, 0.7, 0.6]],
                model_id="test_model",
                inference_time=0.1
            )
        ]
        
        actual_results = [[1, 2, 7, 8]]  # 2 совпадения
        
        # Выполняем анализ
        result = self.learning_system.analyze_prediction_accuracy(
            predictions, actual_results
        )
        
        # Проверяем результаты
        assert isinstance(result, AnalysisResult)
        assert 'performance_metrics' in result.dict()
        assert 'error_patterns' in result.dict()
        assert 'recommendations' in result.dict()
        assert 'timestamp' in result.dict()

    def test_adjust_ensemble_weights(self):
        """Тест корректировки весов ансамбля"""
        # Создаем результат анализа с рекомендациями
        analysis_result = AnalysisResult(
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
        
        # Настраиваем mock для set_predictor_weight
        self.mock_ensemble.set_predictor_weight = Mock()
        
        # Выполняем корректировку
        result = self.learning_system.adjust_ensemble_weights(analysis_result)
        
        # Проверяем что веса были установлены
        assert result == True
        assert self.mock_ensemble.set_predictor_weight.call_count == 3

    def test_get_performance_stats(self):
        """Тест получения статистики производительности"""
        stats = self.learning_system.get_performance_stats()
        
        assert isinstance(stats, dict)
        assert 'total_analyses' in stats
        assert 'recent_accuracy_avg' in stats
        assert 'trend' in stats

    def test_get_learning_recommendations(self):
        """Тест генерации рекомендаций"""
        recommendations = self.learning_system.get_learning_recommendations()
        
        assert isinstance(recommendations, list)
        # Должны быть рекомендации даже без данных
        assert len(recommendations) > 0

    def test_learning_history_persistence(self):
        """Тест сохранения и загрузки истории обучения"""
        with tempfile.TemporaryDirectory() as tmp_dir:
            learning_path = Path(tmp_dir) / 'learning_test.json'
            
            learning_system = SelfLearningSystem(
                self.mock_ensemble,
                {'learning_results_path': learning_path}
            )
            
            # Создаем тестовые данные
            predictions = [
                PredictionResponse(
                    predictions=[[1, 2, 3, 4]],
                    model_id="test",
                    inference_time=0.1
                )
            ]
            actual_results = [[1, 2, 7, 8]]
            
            # Выполняем анализ
            result = learning_system.analyze_prediction_accuracy(
                predictions, actual_results
            )
            
            # Проверяем что файл создан
            assert learning_path.exists()
            
            # Создаем новую систему и проверяем загрузку истории
            new_learning_system = SelfLearningSystem(
                self.mock_ensemble,
                {'learning_results_path': learning_path}
            )
            
            stats = new_learning_system.get_performance_stats()
            assert stats['total_analyses'] == 1


def test_integration_with_ensemble():
    """Интеграционный тест с ансамблевой системой"""
    from ml.ensemble.base_ensemble import WeightedEnsemblePredictor
    
    # Создаем mock ансамбль
    mock_ensemble = Mock(spec=WeightedEnsemblePredictor)
    mock_ensemble.weights = {'test': 1.0}
    mock_ensemble.set_predictor_weight = Mock()
    
    config = {
        'learning_results_path': 'tmp/integration_test.json',
        'max_history_size': 50
    }
    
    # Создаем систему самообучения
    learning_system = SelfLearningSystem(mock_ensemble, config)
    
    # Проверяем интеграцию
    assert learning_system.ensemble == mock_ensemble
    
    # Проверяем что можем получить статистику
    stats = learning_system.get_performance_stats()
    assert isinstance(stats, dict)


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
