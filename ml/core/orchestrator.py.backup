# [file name]: ml/core/orchestrator.py
"""
Оркестратор ML пайплайнов - ПОЛНАЯ РАБОЧАЯ ВЕРСИЯ (ЭТАПЫ 1-8)
"""

import numpy as np
import pandas as pd
from typing import Dict, List, Optional, Any, Tuple
from pathlib import Path
import logging
from datetime import datetime

from .base_model import AbstractBaseModel
from .types import (
    ModelType, ModelStatus, TrainingConfig, 
    DataBatch, PredictionRequest, PredictionResponse,
    TrainingResult, AnalysisResult, DataType
)
from .config_loader import ConfigLoader

from ml.ensemble.base_ensemble import AbstractEnsemblePredictor, WeightedEnsemblePredictor
from ml.features.base import AbstractFeatureEngineer
from ml.data.processors.data_processor import ModularDataProcessor, SimpleDataBatch
from ml.data.providers.dataset_manager import DatasetManager
from ml.data.quality.validators import DataValidator


class MLOrchestrator:
    """
    Оркестратор для управления ML моделями и пайплайнами - ПОЛНАЯ ВЕРСИЯ
    """
    
    def __init__(self, config: Dict[str, Any] = None):
        self.config = config or {}
        self.logger = logging.getLogger(__name__)
        
        # Реестр компонентов
        self._models: Dict[str, AbstractBaseModel] = {}
        self._feature_engineers: Dict[str, AbstractFeatureEngineer] = {}
        self._ensemble_predictors: Dict[str, AbstractEnsemblePredictor] = {}
        self._model_registry: Dict[str, Dict[str, Any]] = {}
        
        # Data Processing компоненты (ЭТАП 8)
        self.data_processor: Optional[ModularDataProcessor] = None
        self.dataset_manager: Optional[DatasetManager] = None  
        self.data_validator: Optional[DataValidator] = None
        
        # Конфигурационный загрузчик
        self._config_loader = ConfigLoader()
        
        # Статистика
        self._training_history: List[Dict[str, Any]] = []
        self._prediction_stats: Dict[str, int] = {}
        
        # Система самообучения
        self.self_learning_system = None
        
        # Автоматическая инициализация из конфига
        if not self.config:
            self._load_default_config()
        
        self._init_components()

    def _load_default_config(self) -> None:
        """Загрузка конфигурации по умолчанию"""
        try:
            component_configs = self._config_loader.load_component_configs()
            self.config = {
                'model': component_configs.get('model', {}),
                'ensemble': component_configs.get('ensemble', {}),
                'learning': component_configs.get('learning', {}),
                'features': component_configs.get('features', {}),
                'data_processing': component_configs.get('data_processing', {})  # ЭТАП 8
            }
            self.logger.info("✅ Конфигурации загружены успешно")
        except Exception as e:
            self.logger.error(f"❌ Ошибка загрузки конфигураций: {e}")
            self.config = {}

    def _init_components(self) -> None:
        """Инициализация всех компонентов системы"""
        self.logger.info("🔄 Инициализация компонентов оркестратора...")
        
        try:
            # Инициализация data processing компонентов ПЕРВЫМИ (ЭТАП 8)
            self._init_data_processing()
            
            # Инициализация feature engineers
            self._init_feature_engineers()
            
            # Инициализация моделей
            self._init_models()
            
            # Инициализация ансамблевых систем
            self._init_ensemble_systems()
            
            # Инициализация системы самообучения
            self._init_self_learning()
            
            self.logger.info("✅ Все компоненты оркестратора инициализированы")
            
        except Exception as e:
            self.logger.error(f"❌ Ошибка инициализации компонентов: {e}")

    def _init_data_processing(self) -> None:
        """Инициализация data processing компонентов (ЭТАП 8)"""
        try:
            data_config = self.config.get('data_processing', {})
            processor_config = data_config.get('processor', {})
            
            # Инициализация Data Processor
            if processor_config:
                class_path = processor_config.get('class')
                params = processor_config.get('params', {})
                
                if class_path:
                    self.logger.info(f"🔄 Создание Data Processor: {class_path}")
                    self.data_processor = self._config_loader.create_component(class_path, params)
                else:
                    # Создаем по умолчанию
                    self.data_processor = ModularDataProcessor(
                        history_size=params.get('history_size', 20),
                        feature_engineers=params.get('feature_engineers', ['statistical', 'advanced'])
                    )
            else:
                # Конфигурации нет - создаем по умолчанию
                self.data_processor = ModularDataProcessor()
            
            if self.data_processor:
                self.logger.info("✅ Data Processor инициализирован")
            else:
                self.logger.error("❌ Не удалось создать Data Processor")
            
            # Инициализация Dataset Manager
            dataset_config = data_config.get('dataset_manager', {})
            dataset_path = dataset_config.get('dataset_path')
            self.dataset_manager = DatasetManager(dataset_path)
            self.logger.info("✅ Dataset Manager инициализирован")
            
            # Инициализация Data Validator
            self.data_validator = DataValidator()
            self.logger.info("✅ Data Validator инициализирован")
            
            # Проверка доступности dataset
            dataset_stats = self.dataset_manager.get_dataset_stats()
            self.logger.info(f"📊 Dataset статистика: {dataset_stats['valid_groups']} валидных групп")
            
        except Exception as e:
            self.logger.error(f"❌ Ошибка инициализации data processing: {e}")

    def _init_feature_engineers(self) -> None:
        """Инициализация feature engineers из конфигурации"""
        try:
            feature_config = self.config.get('features', {})
            enabled_engineers = feature_config.get('enabled_engineers', [])
            engineers_config = feature_config.get('engineers', {})
            
            self.logger.info(f"🔧 Загрузка feature engineers: {enabled_engineers}")
            
            for engineer_name in enabled_engineers:
                if engineer_name in engineers_config:
                    engineer_config = engineers_config[engineer_name]
                    class_path = engineer_config.get('class')
                    params = engineer_config.get('params', {})
                    
                    if class_path:
                        self.logger.info(f"🔄 Создание feature engineer: {engineer_name} -> {class_path}")
                        engineer = self._config_loader.create_component(class_path, params)
                        if engineer:
                            self._feature_engineers[engineer_name] = engineer
                            self.logger.info(f"✅ Feature engineer зарегистрирован: {engineer_name}")
                        else:
                            self.logger.error(f"❌ Не удалось создать feature engineer: {engineer_name}")
                else:
                    self.logger.warning(f"⚠️ Конфигурация для feature engineer не найдена: {engineer_name}")
                    
            self.logger.info(f"📊 Зарегистрировано feature engineers: {list(self._feature_engineers.keys())}")
            
        except Exception as e:
            self.logger.error(f"❌ Ошибка инициализации feature engineers: {e}")

    def _init_models(self) -> None:
        """Инициализация моделей из конфигурации"""
        try:
            model_config = self.config.get('model', {})
            
            # Основная модель
            if 'class' in model_config:
                class_path = model_config['class']
                params = model_config.get('params', {})
                
                self.logger.info(f"🔄 Создание основной модели: {class_path}")
                model = self._config_loader.create_component(class_path, params)
                if model and isinstance(model, AbstractBaseModel):
                    self.register_model(model)
                    self.logger.info(f"✅ Основная модель зарегистрирована: {model.model_id}")
                else:
                    self.logger.error(f"❌ Не удалось создать основную модель: {class_path}")
            else:
                self.logger.warning("⚠️ Конфигурация основной модели не найдена")
                
            self.logger.info(f"📊 Зарегистрировано моделей: {list(self._models.keys())}")
            
        except Exception as e:
            self.logger.error(f"❌ Ошибка инициализации моделей: {e}")

    def _init_ensemble_systems(self) -> None:
        """Инициализация ансамблевых систем"""
        try:
            ensemble_config = self.config.get('ensemble', {})
            predictors_config = ensemble_config.get('predictors', {})
            
            self.logger.info(f"🔄 Загрузка ансамблевых предсказателей: {list(predictors_config.keys())}")
            
            for predictor_name, predictor_config in predictors_config.items():
                class_path = predictor_config.get('class')
                params = predictor_config.get('params', {})
                
                if class_path:
                    self.logger.info(f"🔄 Создание ансамблевого предсказателя: {predictor_name} -> {class_path}")
                    predictor = self._config_loader.create_component(class_path, params)
                    if predictor:
                        # Регистрируем как модель если это AbstractBaseModel
                        if isinstance(predictor, AbstractBaseModel):
                            self.register_model(predictor)
                            self.logger.info(f"✅ Модель зарегистрирована: {predictor.model_id}")
                        
                        # Добавляем в ансамблевые предсказатели
                        self._ensemble_predictors[predictor_name] = predictor
                        self.logger.info(f"✅ Ансамблевый предсказатель зарегистрирован: {predictor_name}")
                    else:
                        self.logger.error(f"❌ Не удалось создать предсказатель: {predictor_name}")
                else:
                    self.logger.warning(f"⚠️ Не указан class для предсказателя: {predictor_name}")
            
            self.logger.info(f"📊 Зарегистрировано ансамблевых предсказателей: {list(self._ensemble_predictors.keys())}")
            
        except Exception as e:
            self.logger.error(f"❌ Ошибка инициализации ансамблевых систем: {e}")

    def _init_self_learning(self) -> None:
        """Инициализация системы самообучения"""
        try:
            learning_config = self.config.get('learning', {})
            system_config = learning_config.get('system', {})
            
            if system_config:
                class_path = system_config.get('class')
                params = system_config.get('params', {})
                
                if class_path:
                    self.logger.info(f"🔄 Создание системы самообучения: {class_path}")
                    
                    # Для SelfLearningSystem нужен ансамбль и конфиг
                    ensemble = self._get_main_ensemble()
                    if ensemble:
                        # Создаем экземпляр с правильными параметрами
                        component_class = self._config_loader.dynamic_import(class_path)
                        
                        # ПРАВИЛЬНАЯ ИНИЦИАЛИЗАЦИЯ: ensemble + config
                        config_params = params.get('config', {})
                        self.self_learning_system = component_class(
                            ensemble=ensemble, 
                            config=config_params
                        )
                        
                        self.logger.info("✅ Система самообучения инициализирована")
                    else:
                        self.logger.warning("⚠️ Не найден ансамбль для системы самообучения")
                else:
                    self.logger.warning("⚠️ Не указан class для системы самообучения")
            else:
                self.logger.info("ℹ️ Система самообучения не настроена")
                
        except Exception as e:
            self.logger.error(f"❌ Ошибка инициализации системы самообучения: {e}")

    def _get_main_ensemble(self) -> Optional[AbstractEnsemblePredictor]:
        """Получение основного ансамбля для SelfLearningSystem"""
        try:
            # Ищем WeightedEnsemblePredictor
            for name, predictor in self._ensemble_predictors.items():
                if isinstance(predictor, AbstractEnsemblePredictor):
                    self.logger.info(f"✅ Найден ансамбль для SelfLearningSystem: {name}")
                    return predictor
            
            # Если не нашли в ансамблевых предсказателях, ищем в моделях
            for model_id, model in self._models.items():
                if isinstance(model, AbstractEnsemblePredictor):
                    self.logger.info(f"✅ Найден ансамбль в моделях: {model_id}")
                    return model
            
            self.logger.warning("⚠️ Не найден подходящий ансамбль для SelfLearningSystem")
            return None
            
        except Exception as e:
            self.logger.error(f"❌ Ошибка поиска ансамбля: {e}")
            return None

    # ========== ОСНОВНЫЕ МЕТОДЫ ORCHESTRATOR (ЭТАПЫ 1-7) ==========

    def register_model(self, model: AbstractBaseModel) -> None:
        """Регистрация модели в оркестраторе"""
        model_id = model.model_id
        
        if model_id in self._models:
            self.logger.warning(f"⚠️ Model '{model_id}' уже зарегистрирована, перезаписываю")
            
        self._models[model_id] = model
        self._model_registry[model_id] = {
            'registered_at': datetime.now(),
            'model_type': model.model_type,
            'status': model.status
        }
        
        self.logger.info(f"✅ Модель зарегистрирована: {model_id} (тип: {model.model_type})")

    def train_model(self, model_id: str, data: DataBatch, config: TrainingConfig) -> TrainingResult:
        """Обучение зарегистрированной модели"""
        if model_id not in self._models:
            raise ValueError(f"Model '{model_id}' не найдена в регистре")
            
        model = self._models[model_id]
        self.logger.info(f"Начало обучения модели '{model_id}'")
        
        # Валидация данных
        if not model.validate_features(data.data):
            raise ValueError("Валидация фич не пройдена")
            
        # Обучение
        result = model.train(data, config)
        
        # Обновление регистра
        self._model_registry[model_id].update({
            'status': result.status,
            'last_trained': datetime.now(),
            'training_metrics': result.metrics
        })
        
        # Сохранение истории
        self._training_history.append({
            'model_id': model_id,
            'timestamp': datetime.now(),
            'result': result.model_dump(),
            'config': config.model_dump()
        })
        
        self.logger.info(f"Обучение завершено для модели '{model_id}'")
        return result

    def predict(self, request: PredictionRequest) -> PredictionResponse:
        """Выполнение предсказания"""
        model_id = request.model_id
        
        if model_id not in self._models:
            raise ValueError(f"Model '{model_id}' не найдена в регистре")
            
        model = self._models[model_id]
        
        if not model.is_trained:
            raise ValueError(f"Model '{model_id}' не обучена")
            
        # Создание DataBatch
        data_batch = DataBatch(
            data=request.data if isinstance(request.data, pd.DataFrame) 
                  else pd.DataFrame(request.data),
            batch_id=f"pred_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
            data_type='prediction'
        )
        
        self.logger.info(f"Начало предсказания для модели '{model_id}'")
        
        response = model.predict(data_batch)
        
        # Обновление статистики
        self._prediction_stats[model_id] = self._prediction_stats.get(model_id, 0) + 1
        
        return response

    def get_model_info(self, model_id: str) -> Optional[Dict[str, Any]]:
        """Получение информации о модели"""
        if model_id not in self._model_registry:
            return None
            
        model = self._models.get(model_id)
        info = self._model_registry[model_id].copy()
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
                'is_trained': self._models[model_id].is_trained
            }
            for model_id, info in self._model_registry.items()
        ]

    def save_model(self, model_id: str, path: Path) -> None:
        """Сохранение модели"""
        if model_id not in self._models:
            raise ValueError(f"Model '{model_id}' не найдена")
            
        self._models[model_id].save(path)
        self.logger.info(f"Model '{model_id}' сохранена в {path}")

    def load_model(self, model_id: str, path: Path, model_class: type) -> None:
        """Загрузка модели"""
        model = model_class(model_id=model_id, model_type=ModelType.REGRESSION)
        model.load(path)
        self.register_model(model)
        self.logger.info(f"Model '{model_id}' загружена из {path}")

    def train_model_with_strategy(self, model_id: str, strategy_id: str, data: DataBatch, config: TrainingConfig) -> TrainingResult:
        """Обучение модели с указанной стратегией"""
        if model_id not in self._models:
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
        model = self._models[model_id]
        result = strategy.train(model, data, config)
        
        # Обновляем статус модели в регистре
        self._model_registry[model_id]['status'] = result.status
        self._model_registry[model_id]['last_trained'] = datetime.now()
        
        return result

    def get_feature_engineers(self) -> Dict[str, AbstractFeatureEngineer]:
        """Получение всех feature engineers"""
        return self._feature_engineers.copy()

    def extract_features(self, data: List[int], engineer_names: List[str] = None) -> Dict[str, np.ndarray]:
        """Извлечение фич с использованием зарегистрированных engineers"""
        if engineer_names is None:
            engineer_names = list(self._feature_engineers.keys())
        
        features = {}
        for name in engineer_names:
            if name in self._feature_engineers:
                engineer = self._feature_engineers[name]
                features[name] = engineer.extract_features(data)
        
        return features

    def get_ensemble_predictors(self) -> Dict[str, Any]:
        """Получение ансамблевых предсказателей"""
        return self._ensemble_predictors.copy()

    def ensemble_predict(self, history: List[int], top_k: int = 15) -> List[tuple]:
        """Ансамблевое предсказание через зарегистрированные системы"""
        all_predictions = []
        
        for name, predictor in self._ensemble_predictors.items():
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
                        data_type=DataType.PREDICTION
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
                            
                            if self._is_valid_prediction_group(pred):
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

    def _is_valid_prediction_group(self, prediction) -> bool:
        """Валидация группы предсказания"""
        try:
            if prediction is None:
                return False
            
            if isinstance(prediction, (list, tuple)):
                if len(prediction) == 4:
                    return all(1 <= x <= 26 for x in prediction)
            elif isinstance(prediction, int):
                return 1 <= prediction <= 26
            
            return False
        except:
            return False

    def get_system_status(self) -> Dict[str, Any]:
        """Получение полного статуса системы"""
        return {
            'models_registered': len(self._models),
            'model_ids': list(self._models.keys()),
            'feature_engineers': list(self._feature_engineers.keys()),
            'ensemble_predictors': list(self._ensemble_predictors.keys()),
            'data_processing_initialized': self.data_processor is not None,  # ЭТАП 8
            'self_learning_configured': self.self_learning_system is not None,
            'total_predictions': sum(self._prediction_stats.values()),
            'training_sessions': len(self._training_history),
            'registry_entries': len(self._model_registry)
        }

    def setup_self_learning(self, config: Dict[str, Any] = None) -> None:
        """Настройка системы самообучения"""
        if config:
            # Обновляем конфигурацию и переинициализируем
            learning_config = self.config.get('learning', {})
            learning_config.update(config)
            self.config['learning'] = learning_config
            self._init_self_learning()
        
        if not self.self_learning_system:
            self._init_self_learning()
        
        self.logger.info("✅ Система самообучения настроена")

    def analyze_predictions(self, predictions: List[PredictionResponse], 
                        actual_results: List[List[int]]) -> AnalysisResult:
        """Анализ предсказаний через систему самообучения"""
        if not self.self_learning_system:
            raise ValueError("Self-learning system not initialized")
        
        return self.self_learning_system.analyze_prediction_accuracy(
            predictions, actual_results
        )

    def get_learning_recommendations(self) -> List[str]:
        """Получение рекомендаций по улучшению модели"""
        if not self.self_learning_system:
            return ["🔧 Система самообучения не инициализирована"]
        
        return self.self_learning_system.get_learning_recommendations()

    def get_performance_stats(self) -> Dict[str, Any]:
        """Получение статистики производительности системы"""
        if not self.self_learning_system:
            return {"status": "not_initialized", "message": "Self-learning system not available"}
        
        return self.self_learning_system.get_performance_stats()

    def adjust_ensemble_weights(self, analysis_result: AnalysisResult) -> bool:
        """Корректировка весов ансамбля на основе анализа"""
        if not self.self_learning_system:
            self.logger.warning("⚠️ Self-learning system not available for weight adjustment")
            return False
        
        return self.self_learning_system.adjust_ensemble_weights(analysis_result)

    def clear_registry(self) -> None:
        """Очистка реестра моделей (для тестирования)"""
        self._models.clear()
        self._feature_engineers.clear() 
        self._ensemble_predictors.clear()
        self._model_registry.clear()
        self._training_history.clear()
        self._prediction_stats.clear()
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
        for model_id, model in self._models.items():
            integration_status['models'][model_id] = {
                'registered': True,
                'is_trained': model.is_trained,
                'status': model.status.value,
                'type': type(model).__name__
            }
        
        # Проверка feature engineers
        for name, engineer in self._feature_engineers.items():
            integration_status['feature_engineers'][name] = {
                'registered': True,
                'type': type(engineer).__name__
            }
        
        # Проверка ансамблевых предсказателей
        for name, predictor in self._ensemble_predictors.items():
            integration_status['ensemble_predictors'][name] = {
                'registered': True,
                'type': type(predictor).__name__,
                'has_predict_method': hasattr(predictor, 'predict')
            }
        
        # Проверка системы самообучения
        integration_status['self_learning'] = {
            'configured': self.self_learning_system is not None,
            'type': type(self.self_learning_system).__name__ if self.self_learning_system else None
        }
        
        self.logger.info("✅ Проверка интеграции компонентов завершена")
        return integration_status

    # ========== DATA PROCESSING МЕТОДЫ (ЭТАП 8) ==========

    def prepare_training_data(self) -> Tuple[DataBatch, DataBatch]:
        """Подготовка данных для обучения через Data Processor"""
        if not self.data_processor:
            raise ValueError("Data Processor не инициализирован")
        
        if not self.dataset_manager:
            raise ValueError("Dataset Manager не инициализирован")
        
        try:
            # Загрузка dataset
            groups = self.dataset_manager.load_dataset()
            
            if not groups:
                raise ValueError("Dataset пуст или не загружен")
            
            # Валидация dataset
            validation_stats = self.data_validator.validate_dataset(groups)
            self.logger.info(f"📊 Валидация dataset: {validation_stats['valid_groups']} валидных групп")
            
            if validation_stats['valid_groups'] < 50:
                raise ValueError(f"Недостаточно валидных групп: {validation_stats['valid_groups']} (нужно минимум 50)")
            
            # Подготовка данных обучения
            features_batch, targets_batch = self.data_processor.prepare_training_data(groups)
            
            # Конвертируем SimpleDataBatch в DataBatch
            features_data_batch = DataBatch(
                data=features_batch.data,
                batch_id=features_batch.batch_id,
                data_type=DataType.TRAINING,
                metadata=features_batch.metadata
            )
            
            targets_data_batch = DataBatch(
                data=targets_batch.data,
                batch_id=targets_batch.batch_id,
                data_type=DataType.TRAINING,
                metadata=targets_batch.metadata
            )
            
            if features_data_batch.data.empty or targets_data_batch.data.empty:
                raise ValueError("Не удалось подготовить данные обучения")
            
            self.logger.info(f"✅ Подготовлены данные обучения: {len(features_data_batch.data)} примеров")
            
            return features_data_batch, targets_data_batch
            
        except Exception as e:
            self.logger.error(f"❌ Ошибка подготовки данных обучения: {e}")
            raise

    def create_prediction_features(self, recent_groups: List[str]) -> DataBatch:
        """Создание фич для предсказания через Data Processor"""
        if not self.data_processor:
            raise ValueError("Data Processor не инициализирован")
        
        try:
            # Валидация входных групп
            valid_groups = [group for group in recent_groups if self.data_validator.validate_group(group)]
            
            if not valid_groups:
                raise ValueError("Нет валидных групп для предсказания")
            
            # Создание фич
            prediction_simple_batch = self.data_processor.create_prediction_features(valid_groups)
            
            # Конвертируем SimpleDataBatch в DataBatch
            prediction_batch = DataBatch(
                data=prediction_simple_batch.data,
                batch_id=prediction_simple_batch.batch_id,
                data_type=DataType.PREDICTION,
                metadata=prediction_simple_batch.metadata
            )
            
            if prediction_batch.data.empty:
                raise ValueError("Не удалось создать фичи для предсказания")
            
            self.logger.info(f"✅ Созданы фичи для предсказания из {len(valid_groups)} групп")
            
            return prediction_batch
            
        except Exception as e:
            self.logger.error(f"❌ Ошибка создания фич предсказания: {e}")
            raise

    def add_new_data(self, new_groups: List[str]) -> bool:
        """Добавление новых данных в dataset"""
        if not self.dataset_manager:
            raise ValueError("Dataset Manager не инициализирован")
        
        try:
            # Валидация новых групп
            valid_groups = [group for group in new_groups if self.data_validator.validate_group(group)]
            
            if not valid_groups:
                self.logger.warning("⚠️ Нет валидных групп для добавления")
                return False
            
            # Добавление в dataset
            success = self.dataset_manager.add_groups(valid_groups)
            
            if success:
                self.logger.info(f"✅ Добавлено {len(valid_groups)} новых групп в dataset")
                
                # Обновление статистики
                stats = self.dataset_manager.get_dataset_stats()
                self.logger.info(f"📊 Обновленная статистика: {stats['valid_groups']} валидных групп")
            else:
                self.logger.error("❌ Не удалось добавить новые группы")
            
            return success
            
        except Exception as e:
            self.logger.error(f"❌ Ошибка добавления новых данных: {e}")
            return False

    def get_data_processing_info(self) -> Dict[str, Any]:
        """Информация о data processing компонентах"""
        info = {
            "data_processor_initialized": self.data_processor is not None,
            "dataset_manager_initialized": self.dataset_manager is not None,
            "data_validator_initialized": self.data_validator is not None,
        }
        
        if self.data_processor:
            info.update(self.data_processor.get_feature_info())
        
        if self.dataset_manager:
            info.update(self.dataset_manager.get_dataset_stats())
        
        return info

    def validate_prediction_accuracy(self, predictions: List[Tuple], 
                                   actuals: List[List[int]]) -> Dict[str, Any]:
        """Валидация точности предсказаний через Data Validator"""
        if not self.data_validator:
            raise ValueError("Data Validator не инициализирован")
        
        return self.data_validator.analyze_prediction_accuracy(predictions, actuals)

    def backup_dataset(self) -> bool:
        """Создание бэкапа dataset"""
        if not self.dataset_manager:
            raise ValueError("Dataset Manager не инициализирован")
        
        return self.dataset_manager.backup_dataset()
