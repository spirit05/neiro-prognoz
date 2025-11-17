# [file name]: ml/core/orchestrator.py
"""
Оркестратор ML пайплайнов - ДОПОЛНЕН DATA PROCESSING
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
from ml.data.processors.data_processor import ModularDataProcessor
from ml.data.providers.dataset_manager import DatasetManager
from ml.data.quality.validators import DataValidator


class MLOrchestrator:
    """
    Оркестратор для управления ML моделями и пайплайнами - ДОПОЛНЕН DATA PROCESSING
    """
    
    def __init__(self, config: Dict[str, Any] = None):
        self.config = config or {}
        self.logger = logging.getLogger(__name__)
        
        # Реестр компонентов
        self._models: Dict[str, AbstractBaseModel] = {}
        self._feature_engineers: Dict[str, AbstractFeatureEngineer] = {}
        self._ensemble_predictors: Dict[str, AbstractEnsemblePredictor] = {}
        self._model_registry: Dict[str, Dict[str, Any]] = {}
        
        # Data Processing компоненты
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
        """Загрузка конфигурации по умолчанию - ДОПОЛНЕН DATA PROCESSING"""
        try:
            component_configs = self._config_loader.load_component_configs()
            self.config = {
                'model': component_configs.get('model', {}),
                'ensemble': component_configs.get('ensemble', {}),
                'learning': component_configs.get('learning', {}),
                'features': component_configs.get('features', {}),
                'data_processing': component_configs.get('data_processing', {})
            }
            self.logger.info("✅ Конфигурации загружены успешно")
        except Exception as e:
            self.logger.error(f"❌ Ошибка загрузки конфигураций: {e}")
            self.config = {}

    def _init_components(self) -> None:
        """Инициализация всех компонентов системы - ДОПОЛНЕН DATA PROCESSING"""
        self.logger.info("🔄 Инициализация компонентов оркестратора...")
        
        try:
            # Инициализация data processing компонентов ПЕРВЫМИ
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
        """Инициализация data processing компонентов"""
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
                    
                    if self.data_processor:
                        self.logger.info("✅ Data Processor инициализирован")
                    else:
                        self.logger.error("❌ Не удалось создать Data Processor")
                else:
                    # Создаем по умолчанию
                    self.data_processor = ModularDataProcessor(
                        history_size=params.get('history_size', 20),
                        feature_engineers=params.get('feature_engineers', ['statistical', 'advanced'])
                    )
                    self.logger.info("✅ Data Processor создан по умолчанию")
            else:
                # Конфигурации нет - создаем по умолчанию
                self.data_processor = ModularDataProcessor()
                self.logger.info("✅ Data Processor создан по умолчанию (без конфига)")
            
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
                        if isinstance(predictor, AbstractBaseModel):
                            self.register_model(predictor)
                        
                        self._ensemble_predictors[predictor_name] = predictor
                        self.logger.info(f"✅ Ансамблевый предсказатель зарегистрирован: {predictor_name}")
            
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
                    
                    # Создаем экземпляр
                    component_class = self._config_loader.dynamic_import(class_path)
                    config_params = params.get('config', {})
                    self.self_learning_system = component_class(
                        ensemble=None,  # Упрощаем для тестов
                        config=config_params
                    )
                    
                    self.logger.info("✅ Система самообучения инициализирована")
            else:
                self.logger.info("ℹ️ Система самообучения не настроена")
                
        except Exception as e:
            self.logger.error(f"❌ Ошибка инициализации системы самообучения: {e}")

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
            
            if features_batch.data.empty or targets_batch.data.empty:
                raise ValueError("Не удалось подготовить данные обучения")
            
            self.logger.info(f"✅ Подготовлены данные обучения: {len(features_batch.data)} примеров")
            
            return features_batch, targets_batch
            
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
            prediction_batch = self.data_processor.create_prediction_features(valid_groups)
            
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

    # ОБНОВЛЕНИЕ СУЩЕСТВУЮЩИХ МЕТОДОВ ДЛЯ ИСПОЛЬЗОВАНИЯ DATA PROCESSING

    def train_model_with_strategy(self, model_id: str, strategy_id: str, 
                                data: Optional[DataBatch] = None, 
                                config: Optional[TrainingConfig] = None) -> TrainingResult:
        """Обучение модели с автоматической подготовкой данных если не предоставлены"""
        if model_id not in self._models:
            raise ValueError(f"Model '{model_id}' not found in registry")
        
        # Если данные не предоставлены - подготавливаем автоматически
        if data is None:
            self.logger.info("🔄 Автоматическая подготовка данных обучения...")
            features_batch, targets_batch = self.prepare_training_data()
            data = features_batch  # Используем фичи как данные для обучения
        
        if config is None:
            config = TrainingConfig()
        
        # Остальная логика остается без изменений
        if strategy_id == "basic":
            from ml.training.strategies import BasicTrainingStrategy
            strategy = BasicTrainingStrategy()
        elif strategy_id == "incremental":
            from ml.training.strategies import IncrementalTrainingStrategy
            strategy = IncrementalTrainingStrategy()
        else:
            raise ValueError(f"Unknown strategy: {strategy_id}")
        
        def orchestrator_callback(message, progress=None):
            self.logger.info(f"Прогресс обучения: {message}")
        
        strategy.add_callback(orchestrator_callback)
        
        model = self._models[model_id]
        result = strategy.train(model, data, config)
        
        self._model_registry[model_id]['status'] = result.status
        self._model_registry[model_id]['last_trained'] = datetime.now()
        
        return result

    def ensemble_predict(self, history: List[int], top_k: int = 15) -> List[tuple]:
        """Ансамблевое предсказание с использованием Data Processor для создания фич"""
        all_predictions = []
        
        # Создаем фичи через Data Processor
        try:
            # Преобразуем историю в формат групп для Data Processor
            recent_groups = []
            for i in range(0, len(history) - 3, 4):
                if i + 4 <= len(history):
                    group_str = " ".join(str(x) for x in history[i:i+4])
                    if self.data_validator.validate_group(group_str):
                        recent_groups.append(group_str)
            
            if not recent_groups:
                self.logger.warning("⚠️ Не удалось создать валидные группы из истории")
                return []
            
            # Создаем фичи для предсказания
            prediction_batch = self.create_prediction_features(recent_groups[-5:])  # последние 5 групп
            
            if prediction_batch.data.empty:
                self.logger.error("❌ Не удалось создать фичи для ансамблевого предсказания")
                return []
                
        except Exception as e:
            self.logger.error(f"❌ Ошибка подготовки фич для ансамбля: {e}")
            return []
        
        # Остальная логика ансамблевого предсказания...
        for name, predictor in self._ensemble_predictors.items():
            if hasattr(predictor, 'predict'):
                try:
                    response = predictor.predict(prediction_batch)
                    
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
        
        sorted_predictions = sorted(aggregated.items(), key=lambda x: x[1], reverse=True)
        return sorted_predictions[:top_k]

    def get_system_status(self) -> Dict[str, Any]:
        """Получение полного статуса системы - ДОПОЛНЕН DATA PROCESSING"""
        status = {
            'models_registered': len(self._models),
            'model_ids': list(self._models.keys()),
            'feature_engineers': list(self._feature_engineers.keys()),
            'ensemble_predictors': list(self._ensemble_predictors.keys()),
            'data_processing_initialized': self.data_processor is not None,
            'self_learning_configured': self.self_learning_system is not None,
            'total_predictions': sum(self._prediction_stats.values()),
            'training_sessions': len(self._training_history),
            'registry_entries': len(self._model_registry)
        }
        
        # Добавляем информацию о данных если доступно
        if self.dataset_manager:
            try:
                stats = self.dataset_manager.get_dataset_stats()
                status.update({
                    'dataset_groups': stats['total_groups'],
                    'valid_groups': stats['valid_groups'],
                    'dataset_size_mb': stats['dataset_size_mb']
                })
            except Exception as e:
                self.logger.warning(f"⚠️ Не удалось получить статистику dataset: {e}")
        
        return status
