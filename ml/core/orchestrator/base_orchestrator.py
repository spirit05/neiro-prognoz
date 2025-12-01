# [file name]: ml/core/orchestrator/base_orchestrator.py
"""
Базовый класс оркестратора - общие атрибуты и методы
ИСПРАВЛЕННАЯ ВЕРСИЯ ДЛЯ РЕГИСТРАЦИИ МОДЕЛЕЙ
"""

import numpy as np
import pandas as pd
from typing import Dict, List, Optional, Any, Tuple
from pathlib import Path
import logging
from datetime import datetime

from ml.core.types import (
    ModelType, ModelStatus, TrainingConfig, 
    DataBatch, PredictionRequest, PredictionResponse,
    TrainingResult, AnalysisResult, DataType
)
from ml.core.config_loader import ConfigLoader


class BaseOrchestrator:
    """
    Базовый класс оркестратора - общая логика для всех менеджеров
    ИСПРАВЛЕННАЯ ВЕРСИЯ ДЛЯ РЕГИСТРАЦИИ МОДЕЛЕЙ
    """

    def __init__(self, config: Dict[str, Any] = None):
        self.config = config or {}
        self.logger = logging.getLogger(__name__)
        
        # 🔧 ИСПРАВЛЕНИЕ: Публичные атрибуты вместо приватных
        self.models: Dict[str, Any] = {}
        self.feature_engineers: Dict[str, Any] = {}
        self.ensemble_predictors: Dict[str, Any] = {}
        self.model_registry: Dict[str, Dict[str, Any]] = {}
        
        # Общие компоненты системы
        self._config_loader = ConfigLoader()
        
        # Data Processing компоненты
        self.data_processor = None
        self.dataset_manager = None  
        self.data_validator = None
        
        # Система самообучения
        self.self_learning_system = None
        
        # Статистика
        self.training_history: List[Dict[str, Any]] = []
        self.prediction_stats: Dict[str, int] = {}
        
        # Автоматическая инициализация
        if not self.config:
            self._load_default_config()
        
        # 🔧 ИСПРАВЛЕНИЕ: Вызываем инициализацию компонентов
        self._init_all_components()

    def _init_all_components(self) -> None:
        """Инициализация всех компонентов системы"""
        self.logger.info("🔄 Инициализация всех компонентов оркестратора...")
        
        try:
            # Инициализация data processing компонентов ПЕРВЫМИ
            self._init_data_processing_components()
            
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
    
    def _load_default_config(self) -> None:
        """Загрузка конфигурации по умолчанию"""
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

    def _init_data_processing_components(self) -> None:
        """Инициализация data processing компонентов"""
        try:
            from ml.data.processors.data_processor import ModularDataProcessor
            from ml.data.providers.dataset_manager import DatasetManager
            from ml.data.quality.validators import DataValidator
            
            data_config = self.config.get('data_processing', {})
            processor_config = data_config.get('processor', {})
            
            # Data Processor
            if processor_config:
                class_path = processor_config.get('class')
                params = processor_config.get('params', {})
                
                if class_path:
                    self.data_processor = self._config_loader.create_component(class_path, params)
                else:
                    self.data_processor = ModularDataProcessor(
                        history_size=params.get('history_size', 20),
                        feature_engineers=params.get('feature_engineers', ['statistical', 'advanced'])
                    )
            else:
                self.data_processor = ModularDataProcessor()
            
            # Dataset Manager
            dataset_config = data_config.get('dataset_manager', {})
            dataset_path = dataset_config.get('dataset_path')
            self.dataset_manager = DatasetManager(dataset_path)
            
            # Data Validator
            self.data_validator = DataValidator()
            
            self.logger.info("✅ Data processing компоненты инициализированы")
            
        except Exception as e:
            self.logger.error(f"❌ Ошибка инициализации data processing: {e}")

    def _init_feature_engineers(self) -> None:
        """Инициализация feature engineers"""
        try:
            feature_config = self.config.get('features', {})
            enabled_engineers = feature_config.get('enabled_engineers', [])
            engineers_config = feature_config.get('engineers', {})
            
            for engineer_name in enabled_engineers:
                if engineer_name in engineers_config:
                    engineer_config = engineers_config[engineer_name]
                    class_path = engineer_config.get('class')
                    params = engineer_config.get('params', {})
                    
                    if class_path:
                        engineer = self._config_loader.create_component(class_path, params)
                        if engineer:
                            self.feature_engineers[engineer_name] = engineer
            
            self.logger.info(f"✅ Feature engineers инициализированы: {list(self.feature_engineers.keys())}")
            
        except Exception as e:
            self.logger.error(f"❌ Ошибка инициализации feature engineers: {e}")

    def _init_models(self) -> None:
        """Инициализация моделей"""
        try:
            model_config = self.config.get('model', {})
            
            if 'class' in model_config:
                class_path = model_config['class']
                params = model_config.get('params', {})
                
                model = self._config_loader.create_component(class_path, params)
                if model:
                    self._register_model_internal(model)
                    
        except Exception as e:
            self.logger.error(f"❌ Ошибка инициализации моделей: {e}")

    def _init_ensemble_systems(self) -> None:
        """Инициализация ансамблевых систем"""
        try:
            ensemble_config = self.config.get('ensemble', {})
            predictors_config = ensemble_config.get('predictors', {})
            
            for predictor_name, predictor_config in predictors_config.items():
                class_path = predictor_config.get('class')
                params = predictor_config.get('params', {})
                
                if class_path:
                    predictor = self._config_loader.create_component(class_path, params)
                    if predictor:
                        self.ensemble_predictors[predictor_name] = predictor
                        
            self.logger.info(f"✅ Ансамблевые системы инициализированы: {list(self.ensemble_predictors.keys())}")
            
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
                    ensemble = self._get_main_ensemble()
                    if ensemble:
                        component_class = self._config_loader.dynamic_import(class_path)
                        config_params = params.get('config', {})
                        self.self_learning_system = component_class(
                            ensemble=ensemble, 
                            config=config_params
                        )
                        
        except Exception as e:
            self.logger.error(f"❌ Ошибка инициализации системы самообучения: {e}")

    def _get_main_ensemble(self) -> Optional[Any]:
        """Получение основного ансамбля"""
        try:
            for name, predictor in self.ensemble_predictors.items():
                if hasattr(predictor, 'predict'):
                    return predictor
            
            for model_id, model in self.models.items():
                if hasattr(model, 'combine_predictions'):
                    return model
            
            return None
            
        except Exception as e:
            self.logger.error(f"❌ Ошибка поиска ансамбля: {e}")
            return None

    def _register_model_internal(self, model: Any) -> None:
        """Внутренняя регистрация модели"""
        model_id = getattr(model, 'model_id', str(id(model)))
        
        self.models[model_id] = model
        self.model_registry[model_id] = {
            'registered_at': datetime.now(),
            'model_type': getattr(model, 'model_type', 'unknown'),
            'status': getattr(model, 'status', 'unknown')
        }

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

    def add_training_record(self, record: Dict[str, Any]) -> None:
        """Добавление записи в историю обучения"""
        self.training_history.append(record)

    def increment_prediction_count(self, model_id: str) -> None:
        """Увеличение счетчика предсказаний для модели"""
        self.prediction_stats[model_id] = self.prediction_stats.get(model_id, 0) + 1

    # 🔧 ИСПРАВЛЕНИЕ: Добавляем методы регистрации моделей напрямую
    def register_model_direct(self, model: Any) -> str:
        """Прямая регистрация модели в оркестраторе (без делегирования менеджерам)"""
        model_id = getattr(model, 'model_id', str(id(model)))
        
        if model_id in self.models:
            self.logger.warning(f"⚠️ Модель '{model_id}' уже зарегистрирована, перезаписываю")
        
        self.models[model_id] = model
        self.model_registry[model_id] = {
            'registered_at': datetime.now(),
            'model_type': getattr(model, 'model_type', 'unknown'),
            'status': getattr(model, 'status', 'unknown')
        }
        
        self.logger.info(f"✅ Модель зарегистрирована напрямую в оркестраторе: {model_id}")
        return model_id

    def register_default_models_direct(self) -> None:
        """Прямая регистрация моделей по умолчанию"""
        try:
            from ml.models.base import EnhancedPredictor
            
            # Регистрируем основную модель
            enhanced_model = EnhancedPredictor(model_id="enhanced_predictor_v2")
            self.register_model_direct(enhanced_model)
            
            self.logger.info("✅ Модели по умолчанию зарегистрированы напрямую")
            
        except Exception as e:
            self.logger.error(f"❌ Ошибка прямой регистрации моделей по умолчанию: {e}")
