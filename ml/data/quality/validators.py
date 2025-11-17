# [file name]: ml/data/quality/validators.py
"""
Валидаторы данных для новой архитектуры
"""

from typing import List, Tuple, Dict, Any
import logging


class DataValidator:
    """Валидация данных в новой архитектуре"""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)

    def validate_group(self, group_str: str) -> bool:
        """Валидация группы чисел"""
        try:
            if not isinstance(group_str, str):
                return False
            
            numbers = [int(x) for x in group_str.strip().split()]
            
            # Проверяем формат: 4 числа
            if len(numbers) != 4:
                return False
            
            # Проверяем диапазон чисел
            if not all(1 <= x <= 26 for x in numbers):
                return False
            
            # Проверяем что пары не одинаковые
            if numbers[0] == numbers[1] or numbers[2] == numbers[3]:
                return False
            
            return True
            
        except Exception as e:
            self.logger.debug(f"❌ Невалидная группа: {group_str}, ошибка: {e}")
            return False

    def compare_groups(self, pred_group: Tuple[int, int, int, int], 
                      actual_group: Tuple[int, int, int, int]) -> Dict[str, int]:
        """
        Сравнение двух групп с парным учетом
        Возвращает детальную статистику совпадений
        """
        pred_pair1 = set([pred_group[0], pred_group[1]])
        pred_pair2 = set([pred_group[2], pred_group[3]])
        actual_pair1 = set([actual_group[0], actual_group[1]])
        actual_pair2 = set([actual_group[2], actual_group[3]])
        
        # Совпадения в парах
        pair1_matches = len(pred_pair1.intersection(actual_pair1))
        pair2_matches = len(pred_pair2.intersection(actual_pair2))
        
        # Точные совпадения по позициям
        exact_matches = sum(1 for i in range(4) if pred_group[i] == actual_group[i])
        
        # Общие совпадения (без учета позиций)
        total_unique_matches = len(set(pred_group).intersection(set(actual_group)))
        
        return {
            'total_matches': pair1_matches + pair2_matches,
            'pair1_matches': pair1_matches,
            'pair2_matches': pair2_matches,
            'exact_matches': exact_matches,
            'total_unique_matches': total_unique_matches,
            'is_perfect_match': exact_matches == 4,
            'is_pair_perfect_match': (pair1_matches == 2 and pair2_matches == 2)
        }

    def validate_dataset(self, groups: List[str]) -> Dict[str, Any]:
        """Валидация всего dataset"""
        valid_groups = []
        invalid_groups = []
        validation_errors = {}
        
        for i, group in enumerate(groups):
            if self.validate_group(group):
                valid_groups.append(group)
            else:
                invalid_groups.append({
                    'index': i,
                    'group': group,
                    'error': 'invalid_format'
                })
        
        stats = {
            'total_groups': len(groups),
            'valid_groups': len(valid_groups),
            'invalid_groups': len(invalid_groups),
            'valid_ratio': len(valid_groups) / len(groups) if groups else 0,
            'validation_errors': validation_errors,
            'invalid_examples': invalid_groups[:10]  # первые 10 ошибок для отладки
        }
        
        self.logger.info(f"📊 Валидация dataset: {stats['valid_groups']}/{stats['total_groups']} валидных")
        
        return stats

    def analyze_prediction_accuracy(self, predictions: List[Tuple], 
                                  actuals: List[List[int]]) -> Dict[str, Any]:
        """Анализ точности предсказаний"""
        if len(predictions) != len(actuals):
            self.logger.error("❌ Несовпадение количества предсказаний и фактических данных")
            return {}
        
        results = []
        total_matches = 0
        perfect_matches = 0
        pair_perfect_matches = 0
        
        for i, (pred, actual) in enumerate(zip(predictions, actuals)):
            if isinstance(pred, tuple) and len(pred) == 4 and len(actual) == 4:
                comparison = self.compare_groups(pred, tuple(actual))
                results.append(comparison)
                
                total_matches += comparison['total_matches']
                if comparison['is_perfect_match']:
                    perfect_matches += 1
                if comparison['is_pair_perfect_match']:
                    pair_perfect_matches += 1
        
        total_comparisons = len(results)
        
        accuracy_stats = {
            'total_comparisons': total_comparisons,
            'average_matches': total_matches / total_comparisons if total_comparisons > 0 else 0,
            'perfect_match_rate': perfect_matches / total_comparisons if total_comparisons > 0 else 0,
            'pair_perfect_rate': pair_perfect_matches / total_comparisons if total_comparisons > 0 else 0,
            'total_perfect_matches': perfect_matches,
            'total_pair_perfect_matches': pair_perfect_matches,
            'detailed_results': results
        }
        
        self.logger.info(f"🎯 Анализ точности: {accuracy_stats['average_matches']:.2f} средних совпадений")
        
        return accuracy_stats
