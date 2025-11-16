# /opt/model/ml/learning/analyzers/error_patterns.py
"""
Анализатор паттернов ошибок в прогнозах - ДЛЯ ЭТАПА 6
"""

from typing import Dict, List, Any
from collections import Counter, defaultdict
from ml.core.types import PredictionResponse


class ErrorPatternAnalyzer:
    """Анализатор паттернов ошибок в прогнозах"""
    
    def identify_patterns(self, predictions: List[PredictionResponse],
                         actual_results: List[List[int]]) -> Dict[str, Any]:
        """
        Выявление паттернов и закономерностей в ошибках
        """
        
        patterns = {
            'common_errors': {},
            'number_frequency_analysis': {},
            'range_analysis': {},
            'feature_correlations': {},
            'temporal_patterns': {}
        }
        
        if not predictions or not actual_results:
            return patterns
        
        # Анализ частых ошибок
        patterns['common_errors'] = self._analyze_common_errors(predictions, actual_results)
        
        # Анализ частот чисел
        patterns['number_frequency_analysis'] = self._analyze_number_frequency(predictions, actual_results)
        
        # Анализ диапазонов
        patterns['range_analysis'] = self._analyze_range_patterns(predictions, actual_results)
        
        return patterns
    
    def _analyze_common_errors(self, predictions: List[PredictionResponse],
                             actual_results: List[List[int]]) -> Dict[str, int]:
        """Анализ наиболее частых типов ошибок"""
        
        error_types = Counter()
        
        for pred, actual in zip(predictions, actual_results):
            if not actual:
                continue
                
            # Извлекаем предсказанные числа
            predicted_numbers = []
            for prediction in pred.predictions:
                if isinstance(prediction, (list, tuple)):
                    predicted_numbers.extend(prediction)
                else:
                    predicted_numbers.append(prediction)
            
            predicted_set = set(predicted_numbers[:4])
            actual_set = set(actual)
            
            # Количество совпадений
            matches = len(predicted_set.intersection(actual_set))
            
            # Классификация ошибок
            if matches == 0:
                error_types["no_matches"] += 1
            elif matches == 1:
                error_types["one_match"] += 1
            elif matches >= 2:
                # Успешное предсказание, не считаем ошибкой
                pass
            
            # Анализ пропущенных чисел
            missed_numbers = actual_set - predicted_set
            if missed_numbers:
                error_types["missed_numbers"] += len(missed_numbers)
            
            # Анализ лишних чисел
            extra_numbers = predicted_set - actual_set
            if extra_numbers:
                error_types["extra_numbers"] += len(extra_numbers)
        
        return dict(error_types)
    
    def _analyze_number_frequency(self, predictions: List[PredictionResponse],
                                actual_results: List[List[int]]) -> Dict[str, Any]:
        """Анализ частотности чисел в ошибках"""
        
        predicted_freq = Counter()
        actual_freq = Counter()
        error_freq = Counter()
        
        for pred, actual in zip(predictions, actual_results):
            if not actual:
                continue
                
            # Частоты в предсказаниях
            for prediction in pred.predictions:
                if isinstance(prediction, (list, tuple)):
                    for num in prediction:
                        predicted_freq[num] += 1
                else:
                    predicted_freq[prediction] += 1
            
            # Частоты в фактических результатах
            for num in actual:
                actual_freq[num] += 1
            
            # Числа, которые были пропущены (ошибки пропуска)
            predicted_numbers = []
            for prediction in pred.predictions:
                if isinstance(prediction, (list, tuple)):
                    predicted_numbers.extend(prediction)
                else:
                    predicted_numbers.append(prediction)
            
            predicted_set = set(predicted_numbers[:4])
            actual_set = set(actual)
            missed_numbers = actual_set - predicted_set
            
            for num in missed_numbers:
                error_freq[f"missed_{num}"] += 1
            
            # Числа, которые были лишними (ошибки включения)
            extra_numbers = predicted_set - actual_set
            for num in extra_numbers:
                error_freq[f"extra_{num}"] += 1
        
        return {
            'predicted_frequencies': dict(predicted_freq),
            'actual_frequencies': dict(actual_freq),
            'error_frequencies': dict(error_freq),
            'discrepancy_analysis': self._calculate_frequency_discrepancy(predicted_freq, actual_freq)
        }
    
    def _calculate_frequency_discrepancy(self, predicted_freq: Counter, 
                                       actual_freq: Counter) -> Dict[str, Any]:
        """Расчет расхождений в частотах"""
        
        all_numbers = set(predicted_freq.keys()).union(set(actual_freq.keys()))
        discrepancies = {}
        
        for num in all_numbers:
            pred_count = predicted_freq.get(num, 0)
            actual_count = actual_freq.get(num, 0)
            
            if actual_count > 0:
                discrepancy = (pred_count - actual_count) / actual_count
                discrepancies[str(num)] = {
                    'predicted_count': pred_count,
                    'actual_count': actual_count,
                    'discrepancy_ratio': discrepancy
                }
        
        return discrepancies
    
    def _analyze_range_patterns(self, predictions: List[PredictionResponse],
                              actual_results: List[List[int]]) -> Dict[str, Any]:
        """Анализ паттернов по диапазонам чисел"""
        
        range_analysis = {
            'low_range': {'predicted': 0, 'actual': 0, 'errors': 0},
            'mid_range': {'predicted': 0, 'actual': 0, 'errors': 0},
            'high_range': {'predicted': 0, 'actual': 0, 'errors': 0}
        }
        
        for pred, actual in zip(predictions, actual_results):
            if not actual:
                continue
                
            # Анализ диапазонов для предсказанных чисел
            for prediction in pred.predictions:
                if isinstance(prediction, (list, tuple)):
                    for num in prediction:
                        if num <= 20:
                            range_analysis['low_range']['predicted'] += 1
                        elif num <= 40:
                            range_analysis['mid_range']['predicted'] += 1
                        else:
                            range_analysis['high_range']['predicted'] += 1
                else:
                    num = prediction
                    if num <= 20:
                        range_analysis['low_range']['predicted'] += 1
                    elif num <= 40:
                        range_analysis['mid_range']['predicted'] += 1
                    else:
                        range_analysis['high_range']['predicted'] += 1
            
            # Анализ диапазонов для фактических чисел
            for num in actual:
                if num <= 20:
                    range_analysis['low_range']['actual'] += 1
                elif num <= 40:
                    range_analysis['mid_range']['actual'] += 1
                else:
                    range_analysis['high_range']['actual'] += 1
            
            # Анализ ошибок по диапазонам
            predicted_numbers = []
            for prediction in pred.predictions:
                if isinstance(prediction, (list, tuple)):
                    predicted_numbers.extend(prediction)
                else:
                    predicted_numbers.append(prediction)
            
            predicted_set = set(predicted_numbers[:4])
            actual_set = set(actual)
            
            for num in actual_set - predicted_set:  # Пропущенные числа
                if num <= 20:
                    range_analysis['low_range']['errors'] += 1
                elif num <= 40:
                    range_analysis['mid_range']['errors'] += 1
                else:
                    range_analysis['high_range']['errors'] += 1
        
        return range_analysis
