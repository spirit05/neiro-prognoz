# [file name]: ml/core/orchestrator/managers/model_manager.py
"""
ModelManager - управление моделями и обучением
"""

import numpy as np
import pandas as pd
from typing import Dict, List, Optional, Any
from pathlib import Path
import logging
from datetime import datetime

from ml.core.types import (
    ModelType, ModelStatus, TrainingConfig, 
    DataBatch, PredictionRequest, PredictionResponse,
    TrainingResult, AnalysisResult
)
from ml.core.base_model import AbstractBaseModel


class ModelManager:
    """Менеджер моделей - обучение, предсказание, управление моделями"""
    
    def __init__(self, orchestrator):
        self.orchestrator = orchestrator
        self.logger = logging.getLogger(__name__)
        
        self.logger.info("✅ ModelManager инициализирован")

    def register_model(self, model: AbstractBaseModel) -> None:
        """Регистрация модели в системе"""
        model_id = model.model_id
        
        if model_id in self.orchestrator.models:
            self.logger.warning(f"⚠️ Model '{model_id}' уже зарегистрирована, перезаписываю")
            
        self.orchestrator.models[model_id] = model
        self.orchestrator.model_registry[model_id] = {
            'registered_at': datetime.now(),
            'model_type': model.model_type,
            'status': model.status
        }
        
        self.logger.info(f"✅ Модель зарегистрирована: {model_id} (тип: {model.model_type})")

    def train_model(self, model_id: str, data: DataBatch, config: TrainingConfig) -> TrainingResult:
        """Обучение зарегистрированной модели"""
        if model_id not in self.orchestrator.models:
            raise ValueError(f"Model '{model_id}' не найдена в регистре")
            
        model = self.orchestrator.models[model_id]
        self.logger.info(f"🔄 Начало обучения модели '{model_id}'")
        
        # Валидация данных
        if not model.validate_features(data.data):
            raise ValueError("Валидация фич не пройдена")
            
        # Обучение
        result = model.train(data, config)
        
        # Обновление регистра
        self.orchestrator.model_registry[model_id].update({
            'status': result.status,
            'last_trained': datetime.now(),
            'training_metrics': result.metrics
        })
        
        # Сохранение истории
        self.orchestrator.add_training_record({
            'model_id': model_id,
            'timestamp': datetime.now(),
            'result': result.model_dump(),
            'config': config.model_dump()
        })
        
        self.logger.info(f"✅ Обучение завершено для модели '{model_id}'")
        return result

    def predict(self, request: PredictionRequest) -> PredictionResponse:
        """Выполнение предсказания"""
        model_id = request.model_id
        
        if model_id not in self.orchestrator.models:
            raise ValueError(f"Model '{model_id}' не найдена в регистре")
            
        model = self.orchestrator.models[model_id]
        
        if not model.is_trained:
            raise ValueError(f"Model '{model_id}' не обучена")
            
        # Создание DataBatch
        data_batch = DataBatch(
            data=request.data if isinstance(request.data, pd.DataFrame) 
                  else pd.DataFrame(request.data),
            batch_id=f"pred_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
            data_type='prediction'
        )
        
        self.logger.info(f"🔄 Начало предсказания для модели '{model_id}'")
        
        response = model.predict(data_batch)
        
        # Обновление статистики
        self.orchestrator.increment_prediction_count(model_id)
        
        return response

    def get_model_info(self, model_id: str) -> Optional[Dict[str, Any]]:
        """Получение информации о модели"""
        if model_id not in self.orchestrator.model_registry:
            return None
            
        model = self.orchestrator.models.get(model_id)
        info = self.orchestrator.model_registry[model_id].copy()
        info['model_id'] = model_id
        
        if model:
            info.update({
                'metadata': model.metadata.model_dump(),
                'is_trained': model.is_trained,
                'feature_specs': [spec.model_dump() for spec in getattr(model, '_feature_specs', [])]
            })
            
        return info

    def list_models(self) -> List[Dict[str, Any]]:
        """Список всех зарегистрированных моделей"""
        return [
            {
                'model_id': model_id,
                'model_type': info['model_type'].value,
                'status': info['status'].value,
                'registered_at': info['registered_at'],
                'is_trained': self.orchestrator.models[model_id].is_trained
            }
            for model_id, info in self.orchestrator.model_registry.items()
        ]

    def save_model(self, model_id: str, path: Path) -> None:
        """Сохранение модели"""
        if model_id not in self.orchestrator.models:
            raise ValueError(f"Model '{model_id}' не найдена")
            
        self.orchestrator.models[model_id].save(path)
        self.logger.info(f"💾 Model '{model_id}' сохранена в {path}")

    def load_model(self, model_id: str, path: Path, model_class: type) -> None:
        """Загрузка модели"""
        model = model_class(model_id=model_id, model_type=ModelType.REGRESSION)
        model.load(path)
        self.register_model(model)
        self.logger.info(f"📥 Model '{model_id}' загружена из {path}")

    def get_feature_engineers(self) -> Dict[str, Any]:
        """Получение всех feature engineers"""
        return self.orchestrator.feature_engineers.copy()

    def extract_features(self, data: List[int], engineer_names: List[str] = None) -> Dict[str, np.ndarray]:
        """Извлечение фич с использованием зарегистрированных engineers"""
        if engineer_names is None:
            engineer_names = list(self.orchestrator.feature_engineers.keys())
        
        features = {}
        for name in engineer_names:
            if name in self.orchestrator.feature_engineers:
                engineer = self.orchestrator.feature_engineers[name]
                features[name] = engineer.extract_features(data)
        
        return features

    def get_ensemble_predictors(self) -> Dict[str, Any]:
        """Получение ансамблевых предсказателей"""
        return self.orchestrator.ensemble_predictors.copy()

    def ensemble_predict(self, history: List[int], top_k: int = 15) -> List[tuple]:
        """Ансамблевое предсказание через зарегистрированные системы"""
        all_predictions = []
        
        for name, predictor in self.orchestrator.ensemble_predictors.items():
            if hasattr(predictor, 'predict'):
                try:
                    # Создаем DataFrame с историей в правильном формате
                    if history:
                        features = {}
                        for i in range(min(50, len(history))):
                            features[f'feature_{i}'] = [float(history[i])] if i < len(history) else [0.0]
                        
                        for i in range(len(history), 50):
                            features[f'feature_{i}'] = [0.0]
                        
                        data_df = pd.DataFrame(features)
                    else:
                        features = {f'feature_{i}': [0.0] for i in range(50)}
                        data_df = pd.DataFrame(features)
                    
                    data_batch = DataBatch(
                        data=data_df,
                        batch_id=f"ensemble_{name}_{datetime.now().strftime('%H%M%S')}",
                        data_type='prediction'
                    )
                    
                    # Вызываем predict с DataBatch
                    response = predictor.predict(data_batch)
                    
                    # Обрабатываем ответ
                    if hasattr(response, 'predictions') and response.predictions:
                        for i, pred in enumerate(response.predictions):
                            score = 0.5
                            if hasattr(response, 'probabilities') and response.probabilities:
                                if i < len(response.probabilities):
                                    probs = response.probabilities[i]
                                    if isinstance(probs, (list, tuple)) and len(probs) > 0:
                                        score = max(probs)
                            
                            if self.orchestrator._is_valid_prediction_group(pred):
                                all_predictions.append((pred, score))
                            
                except Exception as e:
                    self.logger.error(f"❌ Ошибка предсказания {name}: {e}")
                    continue
        
        # Агрегация результатов
        aggregated = {}
        for group, score in all_predictions:
            group_key = tuple(group) if isinstance(group, (list, tuple)) else group
            
            if group_key in aggregated:
                aggregated[group_key] += score
            else:
                aggregated[group_key] = score
        
        # Сортировка и возврат
        sorted_predictions = sorted(aggregated.items(), key=lambda x: x[1], reverse=True)
        return sorted_predictions[:top_k]

    def setup_self_learning(self, config: Dict[str, Any] = None) -> None:
        """Настройка системы самообучения"""
        if config:
            # Обновляем конфигурацию и переинициализируем
            learning_config = self.orchestrator.config.get('learning', {})
            learning_config.update(config)
            self.orchestrator.config['learning'] = learning_config
            self.orchestrator._init_self_learning()
        
        if not self.orchestrator.self_learning_system:
            self.orchestrator._init_self_learning()
        
        self.logger.info("✅ Система самообучения настроена")

    def analyze_predictions(self, predictions: List[PredictionResponse], 
                          actual_results: List[List[int]]) -> AnalysisResult:
        """Анализ предсказаний через систему самообучения"""
        if not self.orchestrator.self_learning_system:
            raise ValueError("Self-learning system not initialized")
        
        return self.orchestrator.self_learning_system.analyze_prediction_accuracy(
            predictions, actual_results
        )

    def get_learning_recommendations(self) -> List[str]:
        """Получение рекомендаций по улучшению модели"""
        if not self.orchestrator.self_learning_system:
            return ["🔧 Система самообучения не инициализирована"]
        
        return self.orchestrator.self_learning_system.get_learning_recommendations()

    def get_performance_stats(self) -> Dict[str, Any]:
        """Получение статистики производительности системы"""
        if not self.orchestrator.self_learning_system:
            return {"status": "not_initialized", "message": "Self-learning system not available"}
        
        return self.orchestrator.self_learning_system.get_performance_stats()

    def adjust_ensemble_weights(self, analysis_result: AnalysisResult) -> bool:
        """Корректировка весов ансамбля на основе анализа"""
        if not self.orchestrator.self_learning_system:
            self.logger.warning("⚠️ Self-learning system not available for weight adjustment")
            return False
        
        return self.orchestrator.self_learning_system.adjust_ensemble_weights(analysis_result)

    def train_model_with_strategy(self, model_id: str, strategy_id: str, data: DataBatch, config: TrainingConfig) -> TrainingResult:
        """Обучение модели с указанной стратегией"""
        if model_id not in self.orchestrator.models:
            raise ValueError(f"Model '{model_id}' not found in registry")
        
        # Динамическая загрузка стратегии
        if strategy_id == "basic":
            from ml.training.strategies import BasicTrainingStrategy
            strategy = BasicTrainingStrategy()
        elif strategy_id == "incremental":
            from ml.training.strategies import IncrementalTrainingStrategy
            strategy = IncrementalTrainingStrategy()
        else:
            raise ValueError(f"Unknown strategy: {strategy_id}")
        
        # Добавляем callbacks оркестратора
        def orchestrator_callback(message, progress=None):
            self.logger.info(f"Прогресс обучения: {message}")
        
        strategy.add_callback(orchestrator_callback)
        
        # Запуск обучения
        model = self.orchestrator.models[model_id]
        result = strategy.train(model, data, config)
        
        # Обновляем статус модели в регистре
        self.orchestrator.model_registry[model_id]['status'] = result.status
        self.orchestrator.model_registry[model_id]['last_trained'] = datetime.now()
        
        return result

    def clear_registry(self) -> None:
        """Очистка реестра моделей (для тестирования)"""
        self.orchestrator.models.clear()
        self.orchestrator.feature_engineers.clear() 
        self.orchestrator.ensemble_predictors.clear()
        self.orchestrator.model_registry.clear()
        self.orchestrator.training_history.clear()
        self.orchestrator.prediction_stats.clear()
        self.logger.info("🧹 Реестр оркестратора очищен")

    def check_component_integration(self) -> Dict[str, Any]:
        """Проверка интеграции всех компонентов"""
        integration_status = {
            'models': {},
            'feature_engineers': {},
            'ensemble_predictors': {},
            'self_learning': {},
            'overall': 'SUCCESS'
        }
        
        # Проверка моделей
        for model_id, model in self.orchestrator.models.items():
            integration_status['models'][model_id] = {
                'registered': True,
                'is_trained': model.is_trained,
                'status': model.status.value,
                'type': type(model).__name__
            }
        
        # Проверка feature engineers
        for name, engineer in self.orchestrator.feature_engineers.items():
            integration_status['feature_engineers'][name] = {
                'registered': True,
                'type': type(engineer).__name__
            }
        
        # Проверка ансамблевых предсказателей
        for name, predictor in self.orchestrator.ensemble_predictors.items():
            integration_status['ensemble_predictors'][name] = {
                'registered': True,
                'type': type(predictor).__name__,
                'has_predict_method': hasattr(predictor, 'predict')
            }
        
        # Проверка системы самообучения
        integration_status['self_learning'] = {
            'configured': self.orchestrator.self_learning_system is not None,
            'type': type(self.orchestrator.self_learning_system).__name__ if self.orchestrator.self_learning_system else None
        }
        
        self.logger.info("✅ Проверка интеграции компонентов завершена")
        return integration_status
