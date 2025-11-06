# ml/learning/self_learning.py
"""
Система самообучения - РЕАЛЬНАЯ РЕАЛИЗАЦИЯ
"""

import json
import os
from datetime import datetime
from typing import Dict, List, Tuple
from config.logging_config import setup_logging
from config.paths import LEARNING_RESULTS
from ml.data.data_loader import compare_groups

logger = setup_logging('SelfLearningSystem')

class SelfLearningSystem:
    def __init__(self):
        self.performance_history = []
        self.accuracy_threshold = 0.3  # Порог точности для адаптации
        self.load_performance_data()
        logger.info("✅ SelfLearningSystem инициализирован")

    def analyze_prediction_accuracy(self, actual_group_str: str) -> Dict:
        """Анализ точности предыдущих предсказаний на основе фактической группы"""
        try:
            # Загружаем последние предсказания
            from ml.data.data_loader import load_predictions
            predictions = load_predictions()

            if not predictions:
                return {
                    'accuracy_score': 0,
                    'matches_count': 0,
                    'total_predictions_analyzed': 0,
                    'message': 'Нет данных предсказаний для анализа'
                }

            # Преобразуем actual_group_str в кортеж чисел
            actual_numbers = [int(x) for x in actual_group_str.strip().split()]
            actual_group = tuple(actual_numbers)

            # Ищем лучшее совпадение среди последних предсказаний
            best_match_score = 0
            best_match_details = {}
            analyzed_count = 0

            for pred_group, score in predictions[:10]:  # Анализируем топ-10 предсказаний
                match_result = compare_groups(pred_group, actual_group)
                total_matches = match_result['total_matches']
                
                # Рассчитываем score совпадения (0-1)
                match_score = total_matches / 4.0
                
                if match_score > best_match_score:
                    best_match_score = match_score
                    best_match_details = {
                        'predicted_group': pred_group,
                        'prediction_score': score,
                        'match_details': match_result
                    }
                
                analyzed_count += 1

            # Сохраняем результат анализа
            analysis_result = {
                'timestamp': datetime.now().isoformat(),
                'actual_group': actual_group,
                'best_match_score': best_match_score,
                'matches_count': best_match_details.get('match_details', {}).get('total_matches', 0),
                'analyzed_predictions_count': analyzed_count,
                'best_prediction': best_match_details.get('predicted_group'),
                'prediction_confidence': best_match_details.get('prediction_score', 0)
            }

            self.performance_history.append(analysis_result)
            self._save_performance_data()

            # Возвращаем упрощенный результат для внешнего использования
            return {
                'accuracy_score': best_match_score,
                'matches_count': analysis_result['matches_count'],
                'total_predictions_analyzed': analyzed_count,
                'best_prediction': analysis_result['best_prediction'],
                'timestamp': analysis_result['timestamp']
            }

        except Exception as e:
            logger.error(f"❌ Ошибка анализа точности: {e}")
            return {
                'accuracy_score': 0,
                'matches_count': 0,
                'error': str(e)
            }

    def get_performance_stats(self) -> Dict:
        """Получение статистики производительности системы самообучения"""
        if not self.performance_history:
            return {
                'recent_accuracy_avg': 0,
                'total_predictions_analyzed': 0,
                'best_accuracy': 0,
                'worst_accuracy': 0,
                'analysis_count': 0,
                'recommendations': ['Недостаточно данных для анализа. Продолжайте использование системы.']
            }

        # Анализируем последние 20 записей
        recent_entries = self.performance_history[-20:]
        accuracy_scores = [entry['best_match_score'] for entry in recent_entries]

        stats = {
            'recent_accuracy_avg': sum(accuracy_scores) / len(accuracy_scores),
            'total_predictions_analyzed': sum(entry['analyzed_predictions_count'] for entry in recent_entries),
            'best_accuracy': max(accuracy_scores) if accuracy_scores else 0,
            'worst_accuracy': min(accuracy_scores) if accuracy_scores else 0,
            'analysis_count': len(recent_entries),
            'performance_history_size': len(self.performance_history)
        }

        # Генерация рекомендаций на основе статистики
        recommendations = self._generate_recommendations(stats)
        stats['recommendations'] = recommendations

        return stats

    def _generate_recommendations(self, stats: Dict) -> List[str]:
        """Генерация рекомендаций на основе статистики производительности"""
        recommendations = []
        
        avg_accuracy = stats['recent_accuracy_avg']
        analysis_count = stats['analysis_count']

        if analysis_count < 5:
            recommendations.append("Накопите больше данных для точного анализа")
        elif avg_accuracy < 0.2:
            recommendations.append("Рассмотрите возможность переобучения модели")
            recommendations.append("Увеличьте разнообразие входных данных")
        elif avg_accuracy < 0.4:
            recommendations.append("Продолжайте сбор данных для улучшения точности")
            recommendations.append("Проверьте качество входных данных")
        else:
            recommendations.append("Система показывает стабильные результаты")
            
        if stats['worst_accuracy'] == 0 and analysis_count > 10:
            recommendations.append("Обнаружены случаи полного несовпадения - проверьте алгоритм предсказаний")

        return recommendations

    def _save_performance_data(self):
        """Сохранение данных о производительности в файл"""
        try:
            data = {
                'performance_history': self.performance_history,
                'last_updated': datetime.now().isoformat(),
                'system_version': '1.0'
            }
            
            os.makedirs(os.path.dirname(LEARNING_RESULTS), exist_ok=True)
            with open(LEARNING_RESULTS, 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
                
            logger.info(f"💾 Данные самообучения сохранены: {len(self.performance_history)} записей")
            
        except Exception as e:
            logger.error(f"❌ Ошибка сохранения данных производительности: {e}")

    def load_performance_data(self):
        """Загрузка данных о производительности из файла"""
        try:
            if os.path.exists(LEARNING_RESULTS):
                with open(LEARNING_RESULTS, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    self.performance_history = data.get('performance_history', [])
                    
                logger.info(f"📂 Загружены данные самообучения: {len(self.performance_history)} записей")
                
        except Exception as e:
            logger.warning(f"⚠️ Ошибка загрузки данных производительности: {e}")
            self.performance_history = []
