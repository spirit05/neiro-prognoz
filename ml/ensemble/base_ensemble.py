# /opt/model/ml/ensemble/base_ensemble.py
"""
ЧИСТАЯ АРХИТЕКТУРА ансамблевой системы - БЕЗ ОБРАТНОЙ СОВМЕСТИМОСТИ
"""

import numpy as np
from typing import List, Tuple, Dict, Optional
from abc import ABC, abstractmethod
import logging
from pathlib import Path

from ml.core.base_model import AbstractBaseModel
from ml.core.types import (
    ModelType, ModelStatus, TrainingConfig, 
    ModelMetadata, TrainingResult, PredictionResponse,
    DataBatch, FeatureSpec
)


class AbstractEnsemblePredictor(AbstractBaseModel, ABC):
    """
    Абстрактный ансамблевый предсказатель - ЧИСТЫЙ ИНТЕРФЕЙС
    """
    
    def __init__(self, model_id: str, model_type: ModelType = ModelType.CLASSIFICATION):
        super().__init__(model_id, model_type)
        self.component_predictors: Dict[str, AbstractBaseModel] = {}
        self.weights: Dict[str, float] = {}
        self._prediction_lock = False
        
        self.logger.info(f"Инициализирован ансамблевый предсказатель: {model_id}")

    @abstractmethod
    def combine_predictions(self, component_results: Dict[str, PredictionResponse]) -> PredictionResponse:
        """Абстрактный метод комбинирования предсказаний"""
        pass

    def add_predictor(self, predictor_id: str, predictor: AbstractBaseModel, weight: float = 1.0) -> None:
        """Добавление предсказателя в ансамбль"""
        self.component_predictors[predictor_id] = predictor
        self.weights[predictor_id] = weight
        self.logger.info(f"✅ Добавлен предсказатель {predictor_id} с весом {weight}")

    def set_predictor_weight(self, predictor_id: str, weight: float) -> None:
        """Установка веса предсказателя"""
        if predictor_id in self.component_predictors:
            self.weights[predictor_id] = weight
            self.logger.info(f"⚖️ Вес {predictor_id} установлен: {weight}")
        else:
            raise ValueError(f"Предсказатель {predictor_id} не найден")

    def train(self, data: DataBatch, config: TrainingConfig) -> TrainingResult:
        """Обучение всех компонентов ансамбля"""
        self.logger.info("🔄 Обучение ансамблевой системы")
        
        training_results = {}
        
        for predictor_id, predictor in self.component_predictors.items():
            try:
                if not predictor.is_trained:
                    result = predictor.train(data, config)
                    training_results[predictor_id] = result
                    self.logger.info(f"✅ {predictor_id} обучен")
                else:
                    self.logger.info(f"⏭️ {predictor_id} уже обучен, пропускаем")
            except Exception as e:
                self.logger.error(f"❌ Ошибка обучения {predictor_id}: {e}")
                raise

        self._is_trained = True
        self.status = ModelStatus.TRAINED
        
        return TrainingResult(
            model_id=self.model_id,
            status=self.status,
            metrics={'component_results': training_results}
        )

    def predict(self, data: DataBatch) -> PredictionResponse:
        """Ансамблевое предсказание - ОСНОВНОЙ МЕТОД НОВОЙ АРХИТЕКТУРЫ"""
        if self._prediction_lock:
            self.logger.warning("⚠️ Обнаружена рекурсия, возвращаем пустой ответ")
            return PredictionResponse(
                predictions=[],
                model_id=self.model_id,
                inference_time=0.0
            )
        
        self._prediction_lock = True
        
        try:
            if not self._is_trained:
                raise ValueError("Ансамбль не обучен")
            
            # Получаем предсказания от всех компонентов
            component_results = {}
            for predictor_id, predictor in self.component_predictors.items():
                if predictor.is_trained:
                    try:
                        response = predictor.predict(data)
                        component_results[predictor_id] = response
                    except Exception as e:
                        self.logger.warning(f"⚠️ Ошибка предсказания {predictor_id}: {e}")
                        continue
            
            # Комбинируем результаты
            ensemble_response = self.combine_predictions(component_results)
            return ensemble_response
            
        finally:
            self._prediction_lock = False

    def save(self, path: Path) -> None:
        """Сохранение ансамбля и всех компонентов"""
        ensemble_config = {
            'model_id': self.model_id,
            'model_type': self.model_type.value,
            'weights': self.weights,
            # 🔧 УБРАНЫ метаданные чтобы избежать проблем с datetime
            'components': list(self.component_predictors.keys())
        }
        
        import json
        config_path = path / f"{self.model_id}_ensemble_config.json"
        with open(config_path, 'w', encoding='utf-8') as f:
            json.dump(ensemble_config, f, indent=2, ensure_ascii=False)
        
        # Сохраняем компоненты
        for predictor_id, predictor in self.component_predictors.items():
            predictor_path = path / predictor_id
            predictor_path.mkdir(exist_ok=True)
            predictor.save(predictor_path)
        
        self.logger.info(f"💾 Ансамбль сохранен: {path}")
          
    def load(self, path: Path) -> None:
        """Загрузка ансамбля и всех компонентов"""
        config_path = path / f"{self.model_id}_ensemble_config.json"
        
        if not config_path.exists():
            raise FileNotFoundError(f"Конфигурация ансамбля не найдена: {config_path}")
        
        import json
        with open(config_path, 'r', encoding='utf-8') as f:
            config = json.load(f)
        
        # Восстанавливаем веса
        self.weights = config.get('weights', {})
        
        # Загружаем компоненты (должны быть предварительно зарегистрированы)
        for predictor_id in config.get('components', []):
            predictor_path = path / predictor_id
            if predictor_id in self.component_predictors and predictor_path.exists():
                self.component_predictors[predictor_id].load(predictor_path)
        
        self._is_trained = True
        self.status = ModelStatus.READY
        self.logger.info(f"📥 Ансамбль загружен: {path}")


class WeightedEnsemblePredictor(AbstractEnsemblePredictor):
    """
    Взвешенный ансамблевый предсказатель - ЧИСТАЯ РЕАЛИЗАЦИЯ
    """
    
    def __init__(self, model_id: str = "weighted_ensemble"):
        super().__init__(model_id)
        self.logger.info("🎯 Инициализирован WeightedEnsemblePredictor")

    def combine_predictions(self, component_results: Dict[str, PredictionResponse]) -> PredictionResponse:
        """Взвешенное комбинирование предсказаний - НОВАЯ ЛОГИКА"""
        if not component_results:
            return PredictionResponse(
                predictions=[],
                model_id=self.model_id,
                inference_time=0.0
            )
        
        # Собираем все предсказания с весами
        all_weighted_predictions = []
        
        for predictor_id, response in component_results.items():
            weight = self.weights.get(predictor_id, 1.0)
            
            for i, prediction in enumerate(response.predictions):
                # Базовый score
                base_score = 1.0
                if response.probabilities and i < len(response.probabilities):
                    # Используем максимальную вероятность как confidence
                    base_score = float(np.max(response.probabilities[i]))
                
                weighted_score = base_score * weight
                all_weighted_predictions.append((prediction, weighted_score))
        
        # Агрегируем по уникальным предсказаниям
        aggregated_scores = {}
        for prediction, score in all_weighted_predictions:
            prediction_key = tuple(prediction) if isinstance(prediction, (list, tuple)) else prediction
            
            if prediction_key in aggregated_scores:
                aggregated_scores[prediction_key] += score
            else:
                aggregated_scores[prediction_key] = score
        
        # Сортируем по убыванию score
        sorted_predictions = sorted(
            [(pred, score) for pred, score in aggregated_scores.items()],
            key=lambda x: x[1],
            reverse=True
        )
        
        # Формируем финальный ответ
        final_predictions = [pred for pred, score in sorted_predictions]
        
        self.logger.info(f"🔀 Скомбинировано {len(final_predictions)} прогнозов от {len(component_results)} моделей")
        
        return PredictionResponse(
            predictions=final_predictions,
            model_id=self.model_id,
            inference_time=0.0
        )

