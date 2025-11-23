# [file name]: ml/core/orchestrator/managers/workflow_manager.py
"""
WorkflowManager - управление сложными операциями и workflow
"""

import time
from typing import List, Dict, Any, Optional
import logging
from datetime import datetime

from ..types.workflow_types import (
    WorkflowResult, WorkflowStatus, SystemOverview, LearningAnalytics
)


class WorkflowManager:
    """Менеджер workflow - сложные операции и бизнес-логика"""

    def __init__(self, orchestrator):
        self.orchestrator = orchestrator
        self.logger = logging.getLogger(__name__)

        self.logger.info("✅ WorkflowManager инициализирован")

    def workflow_add_single_group(self, group: List[int]) -> WorkflowResult:
        """
        Workflow добавления одной группы с полным циклом обработки
        
        Args:
            group: Список из 4 чисел (группа)
            
        Returns:
            WorkflowResult: Результат выполнения workflow
        """
        start_time = time.time()
        steps = []
        
        try:
            self.logger.info("🔄 Запуск workflow добавления одной группы")
            
            # Шаг 1: Валидация группы
            steps.append("validation")
            group_str = " ".join(str(x) for x in group)
            from ml.utils.data_utils import validate_group
            if not validate_group(group_str):
                return WorkflowResult(
                    status=WorkflowStatus.FAILED,
                    message="Невалидная группа",
                    error="Группа должна содержать 4 числа от 1 до 26",
                    steps_completed=steps,
                    execution_time=time.time() - start_time
                )
            
            # Шаг 2: Добавление в dataset
            steps.append("add_to_dataset")
            success = self.orchestrator.data_manager.add_new_data([group_str])
            if not success:
                return WorkflowResult(
                    status=WorkflowStatus.FAILED,
                    message="Ошибка добавления группы",
                    error="Не удалось добавить группу в dataset",
                    steps_completed=steps,
                    execution_time=time.time() - start_time
                )
            
            # Шаг 3: Дообучение модели
            steps.append("retraining")
            try:
                # Создаем DataBatch для новой группы
                features_batch = self.orchestrator.data_manager.create_prediction_features([group_str])
                
                # Получаем основную модель для дообучения
                model_id = list(self.orchestrator.models.keys())[0]  # Берем первую модель
                training_config = self._create_training_config()
                
                # Дообучаем модель
                result = self.orchestrator.model_manager.train_model(
                    model_id, features_batch, training_config
                )
                
                if result.status.value == "failed":
                    return WorkflowResult(
                        status=WorkflowStatus.FAILED,
                        message="Ошибка дообучения",
                        error="Модель не смогла дообучиться на новых данных",
                        steps_completed=steps,
                        execution_time=time.time() - start_time
                    )
                    
            except Exception as e:
                self.logger.error(f"❌ Ошибка дообучения: {e}")
                return WorkflowResult(
                    status=WorkflowStatus.FAILED,
                    message="Ошибка дообучения",
                    error=str(e),
                    steps_completed=steps,
                    execution_time=time.time() - start_time
                )
            
            # Шаг 4: Генерация новых прогнозов
            steps.append("prediction")
            try:
                # Используем последние группы для предсказания
                dataset = self.orchestrator.dataset_manager.load_dataset()
                recent_groups = dataset[-10:]  # Последние 10 групп
                
                prediction_batch = self.orchestrator.data_manager.create_prediction_features(recent_groups)
                request = self._create_prediction_request(prediction_batch)
                predictions = self.orchestrator.model_manager.predict(request)
                
                # Сохраняем прогнозы
                from ml.utils.data_utils import save_predictions
                save_predictions([(pred, 0.5) for pred in predictions.predictions])  # Примерный score
                
            except Exception as e:
                self.logger.warning(f"⚠️ Ошибка генерации прогнозов: {e}")
                # Не прерываем workflow, только логируем
            
            execution_time = time.time() - start_time
            
            return WorkflowResult(
                status=WorkflowStatus.COMPLETED,
                message="Группа успешно добавлена и модель дообучена",
                data={
                    "group_added": group_str,
                    "training_metrics": result.metrics,
                    "predictions_generated": len(predictions.predictions) if 'predictions' in locals() else 0
                },
                steps_completed=steps,
                execution_time=execution_time
            )
            
        except Exception as e:
            self.logger.error(f"❌ Критическая ошибка workflow: {e}")
            return WorkflowResult(
                status=WorkflowStatus.FAILED,
                message="Критическая ошибка выполнения workflow",
                error=str(e),
                steps_completed=steps,
                execution_time=time.time() - start_time
            )

    def workflow_add_multiple_groups(self, groups: List[List[int]], strategy: str = "full_retrain") -> WorkflowResult:
        """
        Workflow добавления нескольких групп
        
        Args:
            groups: Список групп (каждая группа - список из 4 чисел)
            strategy: Стратегия обработки ("full_retrain" или "incremental")
            
        Returns:
            WorkflowResult: Результат выполнения workflow
        """
        start_time = time.time()
        steps = []
        
        try:
            self.logger.info(f"🔄 Запуск workflow добавления {len(groups)} групп (стратегия: {strategy})")
            
            # Шаг 1: Валидация и преобразование групп
            steps.append("validation")
            valid_groups = []
            for group in groups:
                group_str = " ".join(str(x) for x in group)
                from ml.utils.data_utils import validate_group
                if validate_group(group_str):
                    valid_groups.append(group_str)
            
            if not valid_groups:
                return WorkflowResult(
                    status=WorkflowStatus.FAILED,
                    message="Нет валидных групп",
                    error="Все группы не прошли валидацию",
                    steps_completed=steps,
                    execution_time=time.time() - start_time
                )
            
            # Шаг 2: Добавление в dataset
            steps.append("add_to_dataset")
            success = self.orchestrator.data_manager.add_new_data(valid_groups)
            if not success:
                return WorkflowResult(
                    status=WorkflowStatus.FAILED,
                    message="Ошибка добавления групп",
                    error="Не удалось добавить группы в dataset",
                    steps_completed=steps,
                    execution_time=time.time() - start_time
                )
            
            # Шаг 3: Обучение в зависимости от стратегии
            steps.append("training")
            try:
                if strategy == "full_retrain":
                    # Полное переобучение
                    features_batch, targets_batch = self.orchestrator.data_manager.prepare_training_data()
                    model_id = list(self.orchestrator.models.keys())[0]
                    training_config = self._create_training_config()
                    
                    result = self.orchestrator.model_manager.train_model(
                        model_id, features_batch, training_config
                    )
                    
                else:  # incremental
                    # Инкрементальное обучение на новых данных
                    features_batch = self.orchestrator.data_manager.create_prediction_features(valid_groups)
                    model_id = list(self.orchestrator.models.keys())[0]
                    training_config = self._create_training_config()
                    
                    result = self.orchestrator.model_manager.train_model(
                        model_id, features_batch, training_config
                    )
                
                if result.status.value == "failed":
                    return WorkflowResult(
                        status=WorkflowStatus.FAILED,
                        message="Ошибка обучения",
                        error="Модель не смогла обучиться на новых данных",
                        steps_completed=steps,
                        execution_time=time.time() - start_time
                    )
                    
            except Exception as e:
                self.logger.error(f"❌ Ошибка обучения: {e}")
                return WorkflowResult(
                    status=WorkflowStatus.FAILED,
                    message="Ошибка обучения",
                    error=str(e),
                    steps_completed=steps,
                    execution_time=time.time() - start_time
                )
            
            # Шаг 4: Генерация прогнозов
            steps.append("prediction")
            try:
                dataset = self.orchestrator.dataset_manager.load_dataset()
                recent_groups = dataset[-10:]
                
                prediction_batch = self.orchestrator.data_manager.create_prediction_features(recent_groups)
                request = self._create_prediction_request(prediction_batch)
                predictions = self.orchestrator.model_manager.predict(request)
                
                from ml.utils.data_utils import save_predictions
                save_predictions([(pred, 0.5) for pred in predictions.predictions])
                
            except Exception as e:
                self.logger.warning(f"⚠️ Ошибка генерации прогнозов: {e}")
            
            execution_time = time.time() - start_time
            
            return WorkflowResult(
                status=WorkflowStatus.COMPLETED,
                message=f"Успешно добавлено {len(valid_groups)} групп и выполнено {strategy} обучение",
                data={
                    "groups_added": len(valid_groups),
                    "strategy": strategy,
                    "training_metrics": result.metrics,
                    "predictions_generated": len(predictions.predictions) if 'predictions' in locals() else 0
                },
                steps_completed=steps,
                execution_time=execution_time
            )
            
        except Exception as e:
            self.logger.error(f"❌ Критическая ошибка workflow: {e}")
            return WorkflowResult(
                status=WorkflowStatus.FAILED,
                message="Критическая ошибка выполнения workflow",
                error=str(e),
                steps_completed=steps,
                execution_time=time.time() - start_time
            )

    def workflow_full_training_cycle(self) -> WorkflowResult:
        """
        Workflow полного цикла обучения
        
        Returns:
            WorkflowResult: Результат выполнения workflow
        """
        start_time = time.time()
        steps = []
        
        try:
            self.logger.info("🔄 Запуск workflow полного цикла обучения")
            
            # Шаг 1: Подготовка данных
            steps.append("data_preparation")
            features_batch, targets_batch = self.orchestrator.data_manager.prepare_training_data()
            
            # Шаг 2: Обучение всех моделей
            steps.append("training")
            training_results = {}
            for model_id in self.orchestrator.models:
                try:
                    training_config = self._create_training_config()
                    result = self.orchestrator.model_manager.train_model(
                        model_id, features_batch, training_config
                    )
                    training_results[model_id] = result
                except Exception as e:
                    self.logger.error(f"❌ Ошибка обучения модели {model_id}: {e}")
                    training_results[model_id] = {"error": str(e)}
            
            # Шаг 3: Генерация прогнозов
            steps.append("prediction")
            try:
                dataset = self.orchestrator.dataset_manager.load_dataset()
                recent_groups = dataset[-10:]
                
                prediction_batch = self.orchestrator.data_manager.create_prediction_features(recent_groups)
                request = self._create_prediction_request(prediction_batch)
                predictions = self.orchestrator.model_manager.predict(request)
                
                from ml.utils.data_utils import save_predictions
                save_predictions([(pred, 0.5) for pred in predictions.predictions])
                
            except Exception as e:
                self.logger.warning(f"⚠️ Ошибка генерации прогнозов: {e}")
            
            execution_time = time.time() - start_time
            
            return WorkflowResult(
                status=WorkflowStatus.COMPLETED,
                message="Полный цикл обучения завершен",
                data={
                    "models_trained": len(training_results),
                    "training_results": training_results,
                    "predictions_generated": len(predictions.predictions) if 'predictions' in locals() else 0
                },
                steps_completed=steps,
                execution_time=execution_time
            )
            
        except Exception as e:
            self.logger.error(f"❌ Ошибка полного цикла обучения: {e}")
            return WorkflowResult(
                status=WorkflowStatus.FAILED,
                message="Ошибка выполнения полного цикла обучения",
                error=str(e),
                steps_completed=steps,
                execution_time=time.time() - start_time
            )

    def workflow_generate_predictions(self) -> WorkflowResult:
        """
        Workflow генерации прогнозов
        
        Returns:
            WorkflowResult: Результат выполнения workflow
        """
        start_time = time.time()
        steps = []
        
        try:
            self.logger.info("🔄 Запуск workflow генерации прогнозов")
            
            # Шаг 1: Проверка обученности моделей
            steps.append("model_validation")
            trained_models = [
                model_id for model_id, model in self.orchestrator.models.items() 
                if model.is_trained
            ]
            
            if not trained_models:
                return WorkflowResult(
                    status=WorkflowStatus.FAILED,
                    message="Нет обученных моделей",
                    error="Не найдено ни одной обученной модели для генерации прогнозов",
                    steps_completed=steps,
                    execution_time=time.time() - start_time
                )
            
            # Шаг 2: Подготовка данных для предсказания
            steps.append("data_preparation")
            dataset = self.orchestrator.dataset_manager.load_dataset()
            recent_groups = dataset[-10:]  # Последние 10 групп для контекста
            
            prediction_batch = self.orchestrator.data_manager.create_prediction_features(recent_groups)
            
            # Шаг 3: Генерация прогнозов
            steps.append("prediction")
            all_predictions = []
            
            for model_id in trained_models:
                try:
                    request = self._create_prediction_request(prediction_batch, model_id)
                    predictions = self.orchestrator.model_manager.predict(request)
                    all_predictions.extend(predictions.predictions)
                except Exception as e:
                    self.logger.error(f"❌ Ошибка предсказания моделью {model_id}: {e}")
            
            if not all_predictions:
                return WorkflowResult(
                    status=WorkflowStatus.FAILED,
                    message="Не удалось сгенерировать прогнозы",
                    error="Все модели вернули ошибку при предсказании",
                    steps_completed=steps,
                    execution_time=time.time() - start_time
                )
            
            # Шаг 4: Сохранение прогнозов
            steps.append("save_predictions")
            from ml.utils.data_utils import save_predictions
            save_predictions([(pred, 0.5) for pred in all_predictions])
            
            execution_time = time.time() - start_time
            
            return WorkflowResult(
                status=WorkflowStatus.COMPLETED,
                message="Прогнозы успешно сгенерированы",
                data={
                    "models_used": trained_models,
                    "predictions_generated": len(all_predictions),
                    "source_groups": recent_groups
                },
                steps_completed=steps,
                execution_time=execution_time
            )
            
        except Exception as e:
            self.logger.error(f"❌ Ошибка генерации прогнозов: {e}")
            return WorkflowResult(
                status=WorkflowStatus.FAILED,
                message="Ошибка генерации прогнозов",
                error=str(e),
                steps_completed=steps,
                execution_time=time.time() - start_time
            )

    def get_system_overview(self) -> SystemOverview:
        """
        Комплексный обзор системы
        
        Returns:
            SystemOverview: Обзор системы
        """
        try:
            # Статус системы
            system_status = "operational"
            model_status = "trained" if any(m.is_trained for m in self.orchestrator.models.values()) else "not_trained"
            
            # Статус данных
            dataset_stats = self.orchestrator.dataset_manager.get_dataset_stats()
            data_status = "sufficient" if dataset_stats['valid_groups'] >= 50 else "insufficient"
            
            # Статус обучения
            training_status = "completed" if self.orchestrator.training_history else "never"
            last_training = None
            if self.orchestrator.training_history:
                last_training = self.orchestrator.training_history[-1]['timestamp']
            
            # Метрики модели
            model_metrics = {}
            for model_id, model in self.orchestrator.models.items():
                if model.is_trained:
                    model_metrics[model_id] = {
                        'status': model.status.value,
                        'feature_count': len(getattr(model, '_feature_specs', [])),
                        'metadata': model.metadata.model_dump()
                    }
            
            # Производительность
            performance_metrics = {
                'total_predictions': sum(self.orchestrator.prediction_stats.values()),
                'total_training_sessions': len(self.orchestrator.training_history),
                'models_registered': len(self.orchestrator.models)
            }
            
            # Рекомендации
            recommendations = []
            if dataset_stats['valid_groups'] < 100:
                recommendations.append("Добавьте больше данных для улучшения точности")
            if not any(m.is_trained for m in self.orchestrator.models.values()):
                recommendations.append("Выполните обучение модели")
            if not self.orchestrator.prediction_stats:
                recommendations.append("Сгенерируйте прогнозы для тестирования системы")
            
            return SystemOverview(
                system_status=system_status,
                model_status=model_status,
                data_status=data_status,
                training_status=training_status,
                last_training=last_training,
                last_prediction=None,  # Можно добавить из prediction_stats
                total_groups=dataset_stats['total_groups'],
                valid_groups=dataset_stats['valid_groups'],
                model_metrics=model_metrics,
                performance_metrics=performance_metrics,
                recommendations=recommendations
            )
            
        except Exception as e:
            self.logger.error(f"❌ Ошибка получения обзора системы: {e}")
            return SystemOverview(
                system_status="error",
                model_status="unknown",
                data_status="unknown",
                training_status="unknown",
                total_groups=0,
                valid_groups=0,
                recommendations=[f"Ошибка получения обзора: {str(e)}"]
            )

    def get_learning_analytics(self) -> LearningAnalytics:
        """
        Аналитика обучения
        
        Returns:
            LearningAnalytics: Аналитика обучения
        """
        try:
            # Базовая аналитика
            total_training_sessions = len(self.orchestrator.training_history)
            
            # Расчет точности (упрощенно)
            recent_accuracy = 0.0
            best_accuracy = 0.0
            worst_accuracy = 1.0
            total_training_time = 0.0
            
            for session in self.orchestrator.training_history:
                metrics = session['result'].get('metrics', {})
                accuracy = metrics.get('accuracy', 0.0)
                training_time = session['result'].get('training_time', 0.0)
                
                recent_accuracy = accuracy
                best_accuracy = max(best_accuracy, accuracy)
                worst_accuracy = min(worst_accuracy, accuracy)
                total_training_time += training_time
            
            average_training_time = total_training_time / total_training_sessions if total_training_sessions > 0 else 0.0
            
            # Тренд точности (последние 10 сессий)
            prediction_accuracy_trend = [
                session['result'].get('metrics', {}).get('accuracy', 0.0)
                for session in self.orchestrator.training_history[-10:]
            ]
            
            # Важность фич (упрощенно)
            feature_importance = {}
            if self.orchestrator.feature_engineers:
                for name, engineer in self.orchestrator.feature_engineers.items():
                    feature_importance[name] = 1.0 / len(self.orchestrator.feature_engineers)
            
            # Производительность моделей
            model_performance = {}
            for model_id, model in self.orchestrator.models.items():
                if model.is_trained:
                    model_performance[model_id] = {
                        'prediction_count': self.orchestrator.prediction_stats.get(model_id, 0),
                        'status': model.status.value,
                        'last_trained': self.orchestrator.model_registry[model_id].get('last_trained')
                    }
            
            # Кривые обучения (упрощенно)
            learning_curves = {
                'training_loss': [session['result'].get('training_loss', [0.0])[-1] for session in self.orchestrator.training_history],
                'validation_loss': [session['result'].get('validation_loss', [0.0])[-1] for session in self.orchestrator.training_history]
            }
            
            return LearningAnalytics(
                total_training_sessions=total_training_sessions,
                recent_accuracy=recent_accuracy,
                best_accuracy=best_accuracy,
                worst_accuracy=worst_accuracy,
                average_training_time=average_training_time,
                prediction_accuracy_trend=prediction_accuracy_trend,
                feature_importance=feature_importance,
                model_performance=model_performance,
                learning_curves=learning_curves
            )
            
        except Exception as e:
            self.logger.error(f"❌ Ошибка получения аналитики обучения: {e}")
            return LearningAnalytics(
                total_training_sessions=0,
                recent_accuracy=0.0,
                best_accuracy=0.0,
                worst_accuracy=0.0,
                average_training_time=0.0,
                recommendations=[f"Ошибка получения аналитики: {str(e)}"]
            )

    def get_system_status(self) -> Dict[str, Any]:
        """Получение полного статуса системы (для обратной совместимости)"""
        overview = self.get_system_overview()
        analytics = self.get_learning_analytics()
        
        return {
            'models_registered': len(self.orchestrator.models),
            'model_ids': list(self.orchestrator.models.keys()),
            'feature_engineers': list(self.orchestrator.feature_engineers.keys()),
            'ensemble_predictors': list(self.orchestrator.ensemble_predictors.keys()),
            'data_processing_initialized': self.orchestrator.data_processor is not None,
            'self_learning_configured': self.orchestrator.self_learning_system is not None,
            'total_predictions': sum(self.orchestrator.prediction_stats.values()),
            'training_sessions': len(self.orchestrator.training_history),
            'registry_entries': len(self.orchestrator.model_registry),
            'system_overview': overview.model_dump(),
            'learning_analytics': analytics.model_dump()
        }

    def _create_training_config(self):
        """Создание конфигурации обучения"""
        from ml.core.types import TrainingConfig
        return TrainingConfig()

    def _create_prediction_request(self, data_batch, model_id=None):
        """Создание запроса на предсказание"""
        from ml.core.types import PredictionRequest
        
        if model_id is None:
            model_id = list(self.orchestrator.models.keys())[0]
            
        return PredictionRequest(
            data=data_batch.data.to_dict('records'),
            model_id=model_id,
            return_probabilities=True
        )
