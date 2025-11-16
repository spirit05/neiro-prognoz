# /opt/model/ml/learning/analyzers/performance.py
"""
Анализатор производительности моделей - ДЛЯ ЭТАПА 6
"""

import numpy as np
from typing import Dict, List, Any, Tuple
from ml.core.types import PredictionResponse


class PerformanceAnalyzer:
    """Анализатор производительности моделей"""
    
    def analyze(self, predictions: List[PredictionResponse], 
                actual_results: List[List[int]]) -> Dict[str, Any]:
        """
        Анализ точности прогнозов и производительности компонентов
        """
        
        if not predictions or not actual_results:
            return {"error": "No data for analysis"}
        
        metrics = {
            'overall_accuracy': self._calculate_overall_accuracy(predictions, actual_results),
            'component_performance': {},
            'confidence_analysis': {},
            'trend_analysis': {}
        }
        
        # Анализ производительности компонентов ансамбля
        if predictions and hasattr(predictions[0], 'component_predictions'):
            metrics['component_performance'] = self._analyze_component_performance(
                predictions, actual_results
            )
        
        # Анализ уверенности прогнозов
        metrics['confidence_analysis'] = self._analyze_confidence(predictions, actual_results)
        
        # Анализ трендов
        metrics['trend_analysis'] = self._analyze_trends(predictions, actual_results)
        
        return metrics
    
    def _calculate_overall_accuracy(self, predictions: List[PredictionResponse],
                                  actual_results: List[List[int]]) -> float:
        """Расчет общей точности"""
        
        correct_predictions = 0
        total_predictions = 0
        
        for pred, actual in zip(predictions, actual_results):
            if not actual:  # Пропускаем если нет фактических результатов
                continue
                
            # Сравниваем предсказанные числа с фактическими
            predicted_numbers = []
            for prediction in pred.predictions:
                if isinstance(prediction, (list, tuple)) and len(prediction) == 4:
                    predicted_numbers.extend(prediction)
                else:
                    predicted_numbers.append(prediction)
            
            predicted_set = set(predicted_numbers[:4])  # Берем первые 4 числа
            actual_set = set(actual)
            
            # Считаем совпадения
            matches = len(predicted_set.intersection(actual_set))
            
            # Порог точности (например, минимум 2 совпадения из 4)
            required_matches = min(2, len(actual_set))
            if matches >= required_matches:
                correct_predictions += 1
                
            total_predictions += 1
        
        return correct_predictions / total_predictions if total_predictions > 0 else 0.0
    
    def _analyze_component_performance(self, predictions: List[PredictionResponse],
                                     actual_results: List[List[int]]) -> Dict[str, Any]:
        """Анализ производительности компонентов ансамбля"""
        
        component_performance = {}
        
        # Собираем статистику по каждому компоненту
        for i, pred in enumerate(predictions):
            if i >= len(actual_results) or not actual_results[i]:
                continue
                
            actual = set(actual_results[i])
            
            # Проверяем наличие component_predictions
            if hasattr(pred, 'component_predictions') and pred.component_predictions:
                for comp_name, comp_pred in pred.component_predictions.items():
                    if comp_name not in component_performance:
                        component_performance[comp_name] = {
                            'correct': 0,
                            'total': 0,
                            'confidence_sum': 0.0
                        }
                    
                    comp_numbers = []
                    if hasattr(comp_pred, 'predictions'):
                        for prediction in comp_pred.predictions:
                            if isinstance(prediction, (list, tuple)):
                                comp_numbers.extend(prediction)
                            else:
                                comp_numbers.append(prediction)
                    
                    comp_set = set(comp_numbers[:4])
                    matches = len(comp_set.intersection(actual))
                    
                    # Порог точности для компонента
                    required_matches = min(2, len(actual))
                    if matches >= required_matches:
                        component_performance[comp_name]['correct'] += 1
                    
                    component_performance[comp_name]['total'] += 1
                    component_performance[comp_name]['confidence_sum'] += getattr(comp_pred, 'confidence', 0.5)
        
        # Рассчитываем финальные метрики
        for comp_name, stats in component_performance.items():
            if stats['total'] > 0:
                stats['accuracy'] = stats['correct'] / stats['total']
                stats['avg_confidence'] = stats['confidence_sum'] / stats['total']
                # Убираем временные поля
                if 'correct' in stats:
                    del stats['correct']
                if 'confidence_sum' in stats:
                    del stats['confidence_sum']
        
        return component_performance
    
    def _analyze_confidence(self, predictions: List[PredictionResponse],
                          actual_results: List[List[int]]) -> Dict[str, Any]:
        """Анализ корреляции между уверенностью и точностью"""
        
        confidence_buckets = {f"{i/10:.1f}-{(i+1)/10:.1f}": {'correct': 0, 'total': 0} 
                            for i in range(10)}
        
        for pred, actual in zip(predictions, actual_results):
            if not actual:
                continue
                
            confidence = getattr(pred, 'confidence', 0.5)
            bucket_key = f"{confidence//0.1*0.1:.1f}-{confidence//0.1*0.1+0.1:.1f}"
            
            if bucket_key not in confidence_buckets:
                continue
                
            # Проверяем точность предсказания
            predicted_numbers = []
            for prediction in pred.predictions:
                if isinstance(prediction, (list, tuple)):
                    predicted_numbers.extend(prediction)
                else:
                    predicted_numbers.append(prediction)
            
            predicted_set = set(predicted_numbers[:4])
            actual_set = set(actual)
            matches = len(predicted_set.intersection(actual_set))
            required_matches = min(2, len(actual_set))
            
            confidence_buckets[bucket_key]['total'] += 1
            if matches >= required_matches:
                confidence_buckets[bucket_key]['correct'] += 1
        
        # Рассчитываем точность для каждого бакета
        result = {}
        for bucket, stats in confidence_buckets.items():
            if stats['total'] > 0:
                result[bucket] = {
                    'accuracy': stats['correct'] / stats['total'],
                    'sample_size': stats['total']
                }
        
        return result
    
    def _analyze_trends(self, predictions: List[PredictionResponse],
                       actual_results: List[List[int]]) -> Dict[str, Any]:
        """Анализ трендов производительности"""
        
        if len(predictions) < 10:  # Недостаточно данных для анализа трендов
            return {"status": "insufficient_data"}
        
        # Разделяем данные на сегменты для анализа трендов
        segment_size = max(1, len(predictions) // 5)
        segment_accuracies = []
        
        for i in range(0, len(predictions), segment_size):
            segment_pred = predictions[i:i+segment_size]
            segment_actual = actual_results[i:i+segment_size]
            
            accuracy = self._calculate_overall_accuracy(segment_pred, segment_actual)
            segment_accuracies.append(accuracy)
        
        # Анализ тренда
        if len(segment_accuracies) >= 2:
            trend = "improving" if segment_accuracies[-1] > segment_accuracies[0] else "declining"
        else:
            trend = "stable"
        
        return {
            "segment_accuracies": segment_accuracies,
            "trend": trend,
            "latest_accuracy": segment_accuracies[-1] if segment_accuracies else 0.0
        }
