# /opt/model/tests/test_stage6_self_learning.py (исправленная версия)
import pytest
import json
import tempfile
from pathlib import Path
from unittest.mock import Mock

from ml.learning.self_learning import SelfLearningSystem
from ml.learning.analyzers.performance import PerformanceAnalyzer
from ml.learning.analyzers.error_patterns import ErrorPatternAnalyzer
from ml.core.types import PredictionResponse, AnalysisResult


class TestSelfLearningSystem:
    
    def setup_method(self):
        """Настройка тестов"""
        # ✅ ИСПРАВЛЕНИЕ: Создаем mock с реальным словарем weights
        self.mock_ensemble = Mock()
        self.mock_ensemble.weights = {  # ✅ Теперь это реальный dict, а не Mock
            'statistical': 0.4,
            'pattern_based': 0.3,
            'frequency': 0.3
        }
        
        self.config = {
            'learning_results_path': 'tmp/test_learning_results.json',
            'max_history_size': 10,
            'error_threshold': 5
        }
        
        self.self_learning = SelfLearningSystem(self.mock_ensemble, self.config)
    
    def test_initialization(self):
        """Тест инициализации системы самообучения"""
        assert self.self_learning.ensemble == self.mock_ensemble
        assert self.self_learning.config == self.config
        assert isinstance(self.self_learning.performance_analyzer, PerformanceAnalyzer)
        assert isinstance(self.self_learning.error_analyzer, ErrorPatternAnalyzer)
    
    def test_analyze_performance(self):
        """Тест анализа производительности"""
        # Создаем тестовые данные
        predictions = [
            PredictionResponse(
                predictions=[[1, 2, 3, 4]],
                model_id="test_model",
                inference_time=0.1
            )
        ]
        
        actual_results = [[1, 2, 7, 8]]
        
        # Выполняем анализ
        result = self.self_learning.analyze_prediction_accuracy(predictions, actual_results)
        
        # Проверяем результаты
        assert 'performance_metrics' in result.model_dump()
        assert 'error_patterns' in result.model_dump()
        assert 'recommendations' in result.model_dump()
        assert 'timestamp' in result.model_dump()
        assert 'ensemble_weights' in result.model_dump()
    
    def test_get_performance_stats(self):
        """Тест получения статистики производительности"""
        stats = self.self_learning.get_performance_stats()
        
        # Проверяем структуру для случая без данных
        assert isinstance(stats, dict)
        assert 'total_analyses' in stats
        
        # Если данных нет, проверяем структуру no_data
        if stats.get('status') == 'no_data':
            assert 'message' in stats
            assert stats['total_analyses'] == 0
        else:
            # Если данные есть, проверяем полную структуру
            assert 'recent_accuracy_avg' in stats
            assert 'accuracy_stability' in stats
            assert 'trend' in stats
    
    def test_get_performance_stats_with_data(self):
        """Тест получения статистики при наличии данных"""
        # Сначала добавляем тестовые данные
        predictions = [
            PredictionResponse(
                predictions=[[1, 2, 3, 4]],
                model_id="test_model",
                inference_time=0.1
            )
        ]
        
        actual_results = [[1, 2, 7, 8]]
        
        # Выполняем анализ чтобы добавить данные в историю
        result = self.self_learning.analyze_prediction_accuracy(predictions, actual_results)
        assert result is not None
        
        # Теперь получаем статистику
        stats = self.self_learning.get_performance_stats()
        
        # Проверяем полную структуру
        assert isinstance(stats, dict)
        assert 'total_analyses' in stats
        assert 'recent_accuracy_avg' in stats
        assert 'accuracy_stability' in stats
        assert 'trend' in stats
        assert 'last_analysis' in stats
        assert 'active_recommendations' in stats
    
    def test_adjust_ensemble_weights(self):
        """Тест корректировки весов ансамбля"""
        # Создаем mock ансамбль с методом set_predictor_weight
        mock_ensemble = Mock()
        mock_ensemble.set_predictor_weight = Mock()
        mock_ensemble.weights = {'statistical': 0.4, 'pattern_based': 0.3, 'frequency': 0.3}  # ✅ Реальный dict
        
        self_learning = SelfLearningSystem(mock_ensemble, self.config)
        
        # Создаем тестовый результат анализа с рекомендациями
        analysis_result = AnalysisResult(
            timestamp="2024-01-01T00:00:00",
            performance_metrics={},
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
        
        # Выполняем корректировку весов
        result = self_learning.adjust_ensemble_weights(analysis_result)
        
        # Проверяем что веса были установлены
        assert result == True
        assert mock_ensemble.set_predictor_weight.call_count == 3
    
    def test_learning_history_persistence(self):
        """Тест сохранения и загрузки истории обучения"""
        with tempfile.TemporaryDirectory() as tmp_dir:
            # Создаем систему с временным путем
            config = {
                'learning_results_path': Path(tmp_dir) / 'learning_results.json'
            }
            self_learning = SelfLearningSystem(self.mock_ensemble, config)
            
            # Создаем тестовые данные
            predictions = [
                PredictionResponse(
                    predictions=[[1, 2, 3, 4]],
                    model_id="test_model",
                    inference_time=0.1
                )
            ]
            actual_results = [[1, 2, 7, 8]]
            
            # ✅ ИСПРАВЛЕНИЕ: Заменили self_self_learning на self_learning
            result = self_learning.analyze_prediction_accuracy(predictions, actual_results)
            assert result is not None
            
            # Проверяем что файл создан
            assert config['learning_results_path'].exists()
            
            # Загружаем данные из файла
            with open(config['learning_results_path'], 'r') as f:
                saved_data = json.load(f)
            
            # Проверяем структуру сохраненных данных
            assert 'last_analysis' in saved_data
            assert 'analysis_history' in saved_data
            assert len(saved_data['analysis_history']) == 1
    
    def test_get_learning_recommendations(self):
        """Тест получения рекомендаций"""
        # Сначала тестируем без данных
        recommendations = self.self_learning.get_learning_recommendations()
        assert isinstance(recommendations, list)
        
        # Тестируем с данными
        predictions = [
            PredictionResponse(
                predictions=[[1, 2, 3, 4]],
                model_id="test_model",
                inference_time=0.1
            )
        ]
        actual_results = [[1, 2, 7, 8]]
        
        # Выполняем анализ
        self.self_learning.analyze_prediction_accuracy(predictions, actual_results)
        recommendations_with_data = self.self_learning.get_learning_recommendations()
        
        assert isinstance(recommendations_with_data, list)
        assert len(recommendations_with_data) > 0
    
    def test_get_current_weights(self):
        """Тест получения текущих весов"""
        weights = self.self_learning._get_current_weights()
        
        # Должен вернуться реальный словарь
        assert isinstance(weights, dict)
        assert 'statistical' in weights
        assert 'pattern_based' in weights
        assert 'frequency' in weights

class TestPerformanceAnalyzer:
    
    def setup_method(self):
        self.analyzer = PerformanceAnalyzer()
    
    def test_overall_accuracy_calculation(self):
        """Тест расчета общей точности"""
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
        actual_results = [
            [1, 2, 9, 10],  # 2 совпадения - успех
            [11, 12, 13, 14]  # 0 совпадений - неудача
        ]
        
        accuracy = self.analyzer._calculate_overall_accuracy(predictions, actual_results)
        
        # Должна быть 50% точность (1 успех из 2)
        assert accuracy == 0.5
    
    def test_confidence_analysis(self):
        """Тест анализа уверенности"""
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
        actual_results = [
            [1, 2, 9, 10],  # Успех
            [5, 6, 13, 14]   # Успех
        ]
        
        analysis = self.analyzer._analyze_confidence(predictions, actual_results)
        
        # Проверяем структуру анализа уверенности
        assert isinstance(analysis, dict)


class TestErrorPatternAnalyzer:
    
    def setup_method(self):
        self.analyzer = ErrorPatternAnalyzer()
    
    def test_common_errors_analysis(self):
        """Тест анализа частых ошибок"""
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
        actual_results = [
            [1, 9, 10, 11],  # 1 совпадение
            [12, 13, 14, 15]   # 0 совпадений
        ]
        
        errors = self.analyzer._analyze_common_errors(predictions, actual_results)
        
        # Проверяем что ошибки обнаружены
        assert 'one_match' in errors
        assert 'no_matches' in errors

def test_integration_with_ensemble():
    """Интеграционный тест с ансамблевой системой"""
    from ml.ensemble.base_ensemble import WeightedEnsemblePredictor
    
    # Создаем mock ансамбль с реальным словарем weights
    mock_ensemble = Mock(spec=WeightedEnsemblePredictor)
    # ✅ ИСПРАВЛЕНИЕ: Устанавливаем атрибут weights вместо get_weights.return_value
    mock_ensemble.weights = {'test': 1.0}  # Реальный словарь
    
    config = {'learning_results_path': 'tmp/integration_test.json'}
    
    # Создаем систему самообучения
    self_learning = SelfLearningSystem(mock_ensemble, config)
    
    # Проверяем что система корректно интегрирована
    assert self_learning.ensemble == mock_ensemble
    
    # Проверяем что можем получить сводку
    summary = self_learning.get_performance_stats()
    assert isinstance(summary, dict)
    
    # Проверяем работу с данными
    predictions = [
        PredictionResponse(
            predictions=[[1, 2, 3, 4]],
            model_id="test_model",
            inference_time=0.1
        )
    ]
    actual_results = [[1, 2, 7, 8]]
    
    # Проверяем анализ точности
    result = self_learning.analyze_prediction_accuracy(predictions, actual_results)
    assert result is not None
    
    # Проверяем рекомендации
    recommendations = self_learning.get_learning_recommendations()
    assert isinstance(recommendations, list)

if __name__ == "__main__":
    pytest.main([__file__, "-v"])
