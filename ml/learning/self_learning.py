# /opt/model/ml/learning/self_learning.py
"""
ЧИСТАЯ АРХИТЕКТУРА СИСТЕМЫ САМООБУЧЕНИЯ - ЭТАП 6 (ИСПРАВЛЕННАЯ)
"""

import json
import logging
from pathlib import Path
from typing import Dict, List, Optional, Any
from datetime import datetime
import numpy as np

from ml.core.types import PredictionResponse, AnalysisResult, LearningHistory
from ml.ensemble.base_ensemble import AbstractEnsemblePredictor
from ml.learning.analyzers.performance import PerformanceAnalyzer
from ml.learning.analyzers.error_patterns import ErrorPatternAnalyzer


class SelfLearningSystem:
    """
    Модульная система самообучения и анализа производительности
    ЧИСТАЯ АРХИТЕКТУРА - без обратной совместимости
    """
    
    def __init__(self, ensemble: AbstractEnsemblePredictor, config: Dict[str, Any]):
        self.ensemble = ensemble
        self.config = config
        self.logger = logging.getLogger(__name__)
        
        # Модульные анализаторы
        self.performance_analyzer = PerformanceAnalyzer()
        self.error_analyzer = ErrorPatternAnalyzer()
        
        # Конфигурация путей
        self.learning_results_path = Path(config.get(
            'learning_results_path', 
            'data/analytics/learning_results.json'
        ))
        self.learning_results_path.parent.mkdir(parents=True, exist_ok=True)
        
        # Загрузка истории
        self.history = self._load_learning_history()
        
        self.logger.info("✅ Система самообучения инициализирована")

    def analyze_prediction_accuracy(
        self, 
        predictions: List[PredictionResponse],
        actual_results: List[List[int]]
    ) -> AnalysisResult:
        """
        Анализ точности предсказаний - НОВАЯ АРХИТЕКТУРА
        """
        self.logger.info(f"🔍 Анализ точности {len(predictions)} предсказаний")
        
        # Анализ производительности
        performance_metrics = self.performance_analyzer.analyze(
            predictions, actual_results
        )
        
        # Анализ паттернов ошибок
        error_patterns = self.error_analyzer.identify_patterns(
            predictions, actual_results
        )
        
        # Генерация рекомендаций
        recommendations = self._generate_recommendations(
            performance_metrics, error_patterns
        )
        
        # Создание результата анализа
        analysis_result = AnalysisResult(
            timestamp=datetime.now().isoformat(),
            performance_metrics=performance_metrics,
            error_patterns=error_patterns,
            recommendations=recommendations,
            ensemble_weights=self._get_current_weights()
        )
        
        # Сохранение результатов
        self._save_analysis_result(analysis_result)
        
        self.logger.info("✅ Анализ точности завершен")
        return analysis_result

    def adjust_ensemble_weights(self, analysis_result: AnalysisResult) -> bool:
        """
        Корректировка весов ансамбля на основе анализа
        """
        try:
            recommendations = analysis_result.recommendations
            
            if 'weight_adjustments' in recommendations:
                new_weights = recommendations['weight_adjustments']
                
                # Применяем новые веса к ансамблю
                for predictor_id, weight in new_weights.items():
                    if hasattr(self.ensemble, 'set_predictor_weight'):
                        self.ensemble.set_predictor_weight(predictor_id, weight)
                        self.logger.info(f"⚖️ Вес {predictor_id} установлен: {weight}")
                
                return True
            
            self.logger.info("⏭️ Корректировка весов не требуется")
            return False
            
        except Exception as e:
            self.logger.error(f"❌ Ошибка корректировки весов: {e}")
            return False

    def get_performance_stats(self) -> Dict[str, Any]:
        """
        Получение комплексной статистики производительности
        """
        if not self.history.analysis_history:
            return {
                'status': 'no_data',
                'message': 'Нет данных для анализа',
                'total_analyses': 0
            }
        
        # Анализ последних результатов
        recent_analyses = self.history.analysis_history[-10:]
        
        # Расчет метрик
        accuracy_scores = [
            analysis.performance_metrics.get('overall_accuracy', 0)
            for analysis in recent_analyses
        ]
        
        if accuracy_scores:
            avg_accuracy = np.mean(accuracy_scores)
            accuracy_std = np.std(accuracy_scores)
            
            # Анализ тренда
            trend = "stable"
            if len(accuracy_scores) >= 5:
                first_half = accuracy_scores[:len(accuracy_scores)//2]
                second_half = accuracy_scores[len(accuracy_scores)//2:]
                
                if np.mean(second_half) > np.mean(first_half) + 0.1:
                    trend = "improving"
                elif np.mean(second_half) < np.mean(first_half) - 0.1:
                    trend = "declining"
        else:
            avg_accuracy = 0.0
            accuracy_std = 0.0
            trend = "unknown"
        
        return {
            'total_analyses': len(self.history.analysis_history),
            'recent_accuracy_avg': avg_accuracy,
            'accuracy_stability': max(0, 1 - accuracy_std),
            'trend': trend,
            'last_analysis': self.history.last_analysis,
            'active_recommendations': len(
                self.history.analysis_history[-1].recommendations.get('training_suggestions', [])
                if self.history.analysis_history else []
            )
        }

    def get_learning_recommendations(self) -> List[str]:
        """
        Генерация интеллектуальных рекомендаций для улучшения
        """
        recommendations = []
        
        if not self.history.analysis_history:
            return ["📊 Собираем данные для анализа..."]
        
        latest_analysis = self.history.analysis_history[-1]
        performance_metrics = latest_analysis.performance_metrics
        error_patterns = latest_analysis.error_patterns
        
        # Рекомендации на основе точности
        overall_accuracy = performance_metrics.get('overall_accuracy', 0)
        
        if overall_accuracy < 0.2:
            recommendations.append("🚨 **Критически низкая точность** - требуется срочное переобучение")
        elif overall_accuracy < 0.3:
            recommendations.append("⚠️ **Низкая точность** - рекомендуется полное переобучение модели")
        elif overall_accuracy < 0.5:
            recommendations.append("📉 **Средняя точность** - добавьте разнообразные данные для обучения")
        elif overall_accuracy > 0.7:
            recommendations.append("✅ **Высокая точность** - система работает стабильно")
        
        # Рекомендации на основе ошибок
        common_errors = error_patterns.get('common_errors', {})
        if common_errors.get('no_matches', 0) > 5:
            recommendations.append("🎯 **Много промахов** - пересмотрите стратегию генерации кандидатов")
        
        if common_errors.get('missed_numbers', 0) > 10:
            recommendations.append("🔍 **Частые пропуски чисел** - улучшите feature engineering")
        
        # Рекомендации по компонентам ансамбля
        component_performance = performance_metrics.get('component_performance', {})
        if component_performance:
            worst_performer = min(
                component_performance.items(),
                key=lambda x: x[1].get('accuracy', 1)
            )
            if worst_performer[1].get('accuracy', 1) < 0.2:
                recommendations.append(f"🔄 **Слабый компонент {worst_performer[0]}** - рассмотрите замену стратегии")
        
        # Общие рекомендации
        if not recommendations:
            if overall_accuracy > 0.6:
                recommendations.append("⚡ **Продолжайте текущую стратегию** - система работает эффективно")
            else:
                recommendations.append("🔄 **Требуется оптимизация** - рассмотрите fine-tuning модели")
        
        return recommendations[:6]  # Ограничиваем для читабельности

    def _generate_recommendations(
        self, 
        performance_metrics: Dict[str, Any],
        error_patterns: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Генерация комплексных рекомендаций для улучшения
        """
        recommendations = {
            'weight_adjustments': {},
            'training_suggestions': [],
            'feature_improvements': [],
            'strategy_changes': []
        }
        
        # Корректировка весов на основе производительности компонентов
        component_performance = performance_metrics.get('component_performance', {})
        if component_performance:
            total_accuracy = sum(
                comp.get('accuracy', 0) for comp in component_performance.values()
            )
            
            if total_accuracy > 0:
                for component, metrics in component_performance.items():
                    accuracy = metrics.get('accuracy', 0)
                    new_weight = accuracy / total_accuracy
                    recommendations['weight_adjustments'][component] = round(new_weight, 3)
        
        # Рекомендации по обучению
        overall_accuracy = performance_metrics.get('overall_accuracy', 0)
        if overall_accuracy < 0.3:
            recommendations['training_suggestions'].append(
                "Провести полное переобучение на расширенном датасете"
            )
        elif overall_accuracy < 0.5:
            recommendations['training_suggestions'].append(
                "Дообучить модель на новых данных"
            )
        
        # Рекомендации по фичам
        feature_correlations = error_patterns.get('feature_correlations', {})
        for feature, correlation in feature_correlations.items():
            if abs(correlation) > 0.7:
                action = "увеличить" if correlation > 0 else "уменьшить"
                recommendations['feature_improvements'].append(
                    f"{action} влияние фичи: {feature}"
                )
        
        # Стратегические изменения
        confidence_analysis = performance_metrics.get('confidence_analysis', {})
        if confidence_analysis:
            low_confidence_buckets = [
                bucket for bucket, stats in confidence_analysis.items()
                if stats.get('accuracy', 0) < 0.3 and stats.get('sample_size', 0) > 5
            ]
            if low_confidence_buckets:
                recommendations['strategy_changes'].append(
                    "Увеличить порог confidence для фильтрации ненадежных предсказаний"
                )
        
        return recommendations

    def _get_current_weights(self) -> Dict[str, float]:
        """Получение текущих весов ансамбля"""
        if hasattr(self.ensemble, 'weights'):
            return self.ensemble.weights.copy()
        return {}

    def _save_analysis_result(self, analysis_result: AnalysisResult):
        """Сохранение результатов анализа"""
        try:
            # Обновляем историю
            self.history.last_analysis = analysis_result.timestamp
            self.history.analysis_history.append(analysis_result)
            
            # Ограничиваем размер истории
            max_history = self.config.get('max_history_size', 50)
            self.history.analysis_history = self.history.analysis_history[-max_history:]
            
            # Сохраняем в файл
            with open(self.learning_results_path, 'w', encoding='utf-8') as f:
                json.dump(self.history.model_dump(), f, indent=2, ensure_ascii=False)
                
            self.logger.info(f"💾 Результаты анализа сохранены: {self.learning_results_path}")
            
        except Exception as e:
            self.logger.error(f"❌ Ошибка сохранения результатов: {e}")

    def _load_learning_history(self) -> LearningHistory:
        """Загрузка истории обучения"""
        if self.learning_results_path.exists():
            try:
                with open(self.learning_results_path, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                
                # Конвертируем старый формат в новый
                if isinstance(data, list):
                    self.logger.info("🔄 Конвертация старого формата learning_results.json")
                    return self._convert_old_format(data)
                else:
                    return LearningHistory(**data)
                    
            except Exception as e:
                self.logger.warning(f"⚠️ Ошибка загрузки истории: {e}")
        
        # Новая структура по умолчанию
        return LearningHistory(
            last_analysis=None,
            analysis_history=[],
            total_analyses=0
        )

    def _convert_old_format(self, old_data: List[Dict]) -> LearningHistory:
        """
        Конвертация старого формата learning_results.json в новый
        Обеспечивает совместимость с существующими данными
        """
        analysis_history = []
        
        for item in old_data:
            if isinstance(item, dict) and 'predictions_accuracy' in item:
                # Это основной блок с predictions_accuracy
                accuracy_data = item.get('predictions_accuracy', [])
                
                for accuracy_item in accuracy_data:
                    if isinstance(accuracy_item, dict) and 'accuracy_score' in accuracy_item:
                        # Конвертируем запись точности
                        analysis_result = AnalysisResult(
                            timestamp=accuracy_item.get('timestamp', datetime.now().isoformat()),
                            performance_metrics={
                                'overall_accuracy': accuracy_item.get('accuracy_score', 0),
                                'matches_count': accuracy_item.get('matches_count', 0)
                            },
                            error_patterns={},
                            recommendations={},
                            ensemble_weights={}
                        )
                        analysis_history.append(analysis_result)
        
        return LearningHistory(
            last_analysis=analysis_history[-1].timestamp if analysis_history else None,
            analysis_history=analysis_history,
            total_analyses=len(analysis_history)
        )

    def reset_learning_data(self):
        """Сброс данных обучения"""
        self.history = LearningHistory(
            last_analysis=None,
            analysis_history=[],
            total_analyses=0
        )
        self._save_analysis_result(AnalysisResult(
            timestamp=datetime.now().isoformat(),
            performance_metrics={},
            error_patterns={},
            recommendations={},
            ensemble_weights={}
        ))
        self.logger.info("🔄 Данные обучения сброшены")
