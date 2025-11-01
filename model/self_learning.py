# [file name]: model/self_learning.py
"""
Система самообучения на ошибках
"""

import json
import os
from typing import List, Tuple, Dict
from datetime import datetime
from .data_loader import load_dataset, load_predictions, compare_groups

class SelfLearningSystem:
    def __init__(self, results_file: str = "data/learning_results.json"):
        self.results_file = results_file
        self.learning_data = self._load_learning_data()
    
    def _load_learning_data(self) -> Dict:
        """Загрузка данных обучения"""
        if os.path.exists(self.results_file):
            try:
                with open(self.results_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except:
                pass
        return {
            'predictions_accuracy': [],
            'model_performance': {},
            'learning_patterns': {},
            'last_analysis': None
        }
    
    def analyze_prediction_accuracy(self, actual_group: str):
        """Анализ точности последних предсказаний"""
        try:
            actual_numbers = [int(x) for x in actual_group.strip().split()]
            actual_tuple = tuple(actual_numbers)
            
            previous_predictions = load_predictions()
            if not previous_predictions:
                return None
            
            best_match = None
            best_score = 0
            best_prediction = None
            
            # Ищем лучшее совпадение среди предсказаний
            for pred_group, score in previous_predictions:
                comparison = compare_groups(pred_group, actual_tuple)
                total_matches = comparison['total_matches']
                
                if total_matches > best_score:
                    best_score = total_matches
                    best_match = comparison
                    best_prediction = pred_group
            
            # Сохраняем результат анализа
            analysis_result = {
                'timestamp': datetime.now().isoformat(),
                'actual_group': actual_group,
                'best_prediction': best_prediction,
                'matches_count': best_score,
                'comparison_details': best_match,
                'accuracy_score': best_score / 4.0  # Нормализованная точность
            }
            
            self.learning_data['predictions_accuracy'].append(analysis_result)
            self._save_learning_data()
            
            # Анализируем паттерны ошибок
            self._analyze_error_patterns(analysis_result)
            
            return analysis_result
            
        except Exception as e:
            print(f"❌ Ошибка анализа точности: {e}")
            return None
    
    def _analyze_error_patterns(self, analysis_result: Dict):
        """Анализ паттернов ошибок для улучшения предсказаний"""
        accuracy = analysis_result['accuracy_score']
        
        if accuracy < 0.5:  # Низкая точность
            actual_group = analysis_result['actual_group']
            predicted_group = analysis_result['best_prediction']
            
            if predicted_group:
                # Анализируем, какие числа были пропущены
                actual_numbers = [int(x) for x in actual_group.split()]
                predicted_numbers = list(predicted_group)
                
                missed_numbers = set(actual_numbers) - set(predicted_numbers)
                false_numbers = set(predicted_numbers) - set(actual_numbers)
                
                # Сохраняем паттерны ошибок
                if 'error_patterns' not in self.learning_data:
                    self.learning_data['error_patterns'] = []
                
                error_pattern = {
                    'timestamp': analysis_result['timestamp'],
                    'missed_numbers': list(missed_numbers),
                    'false_numbers': list(false_numbers),
                    'accuracy': accuracy
                }
                
                self.learning_data['error_patterns'].append(error_pattern)
    
    def get_learning_recommendations(self) -> List[str]:
        """Получение рекомендаций для улучшения на основе анализа ошибок"""
        recommendations = []
        
        # Анализ частых ошибок
        if 'error_patterns' in self.learning_data:
            error_patterns = self.learning_data['error_patterns'][-20:]  # Последние 20 ошибок
            
            # Анализ часто пропускаемых чисел
            missed_counter = {}
            for pattern in error_patterns:
                for num in pattern.get('missed_numbers', []):
                    missed_counter[num] = missed_counter.get(num, 0) + 1
            
            # Рекомендации на основе анализа
            if missed_counter:
                most_missed = max(missed_counter, key=missed_counter.get)
                recommendations.append(f"⚠️  Часто пропускается число {most_missed} - увеличьте его приоритет")
        
        # Общие рекомендации
        accuracy_data = self.learning_data.get('predictions_accuracy', [])
        if accuracy_data:
            recent_accuracy = [a['accuracy_score'] for a in accuracy_data[-10:]]
            if recent_accuracy:
                avg_accuracy = sum(recent_accuracy) / len(recent_accuracy)
                
                if avg_accuracy < 0.3:
                    recommendations.append("🎯 Низкая точность предсказаний - рекомендуется переобучить модель")
                elif avg_accuracy > 0.7:
                    recommendations.append("✅ Высокая точность - система работает хорошо!")
        
        if not recommendations:
            recommendations.append("📊 Собираем данные для анализа...")
        
        return recommendations
    
    def adjust_ensemble_weights(self, ensemble_predictor) -> bool:
        """Корректировка весов ансамбля на основе производительности"""
        try:
            accuracy_data = self.learning_data.get('predictions_accuracy', [])
            if len(accuracy_data) < 5:  # Нужно достаточно данных
                return False
            
            # Анализ производительности разных стратегий
            recent_accuracy = accuracy_data[-10:]
            accuracy_scores = [a['accuracy_score'] for a in recent_accuracy if 'accuracy_score' in a]
            
            if not accuracy_scores:
                return False
                
            avg_accuracy = sum(accuracy_scores) / len(accuracy_scores)
            
            if avg_accuracy < 0.4:
                # Увеличиваем вес нейросети
                if hasattr(ensemble_predictor, 'weights') and 'neural' in ensemble_predictor.weights:
                    ensemble_predictor.weights['neural'] = min(0.5, ensemble_predictor.weights['neural'] + 0.1)
                    if 'frequency' in ensemble_predictor.weights:
                        ensemble_predictor.weights['frequency'] = max(0.2, ensemble_predictor.weights['frequency'] - 0.05)
                    print("🔧 Скорректированы веса ансамбля в пользу нейросети")
                    return True
                
            return False
            
        except Exception as e:
            print(f"❌ Ошибка корректировки весов: {e}")
            return False
    
    def _save_learning_data(self):
        """Сохранение данных обучения"""
        try:
            os.makedirs(os.path.dirname(self.results_file), exist_ok=True)
            self.learning_data['last_analysis'] = datetime.now().isoformat()
            
            with open(self.results_file, 'w', encoding='utf-8') as f:
                json.dump(self.learning_data, f, ensure_ascii=False, indent=2)
        except Exception as e:
            print(f"❌ Ошибка сохранения данных обучения: {e}")
    
    def get_performance_stats(self) -> Dict:
        """Получение статистики производительности"""
        accuracy_data = self.learning_data.get('predictions_accuracy', [])
        
        if not accuracy_data:
            return {'message': 'Нет данных для анализа'}
        
        recent_accuracy = [a.get('accuracy_score', 0) for a in accuracy_data[-20:] if 'accuracy_score' in a]
        
        if not recent_accuracy:
            return {'message': 'Недостаточно данных для анализа'}
        
        return {
            'total_predictions_analyzed': len(accuracy_data),
            'recent_accuracy_avg': sum(recent_accuracy) / len(recent_accuracy),
            'best_accuracy': max(recent_accuracy),
            'worst_accuracy': min(recent_accuracy),
            'recommendations': self.get_learning_recommendations()
        }
    
    def reset_learning_data(self):
        """Сброс данных обучения"""
        self.learning_data = {
            'predictions_accuracy': [],
            'model_performance': {},
            'learning_patterns': {},
            'last_analysis': None
        }
        self._save_learning_data()
        print("✅ Данные обучения сброшены")