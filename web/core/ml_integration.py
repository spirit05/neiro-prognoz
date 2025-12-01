# [file name]: web/core/ml_integration.py
"""
Интеграция веб-интерфейса с WorkflowManager - ИСПРАВЛЕННАЯ ВЕРСИЯ С ЗАГРУЗКОЙ МОДЕЛИ
"""

import os
import sys
import logging
from typing import Dict, Any, List, Optional, Tuple
import pandas as pd
from ml.core.types import ModelStatus

# Добавляем корневую директорию проекта в путь
project_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, project_root)

from ml.core.orchestrator import MLOrchestrator
from ml.core.orchestrator.types import WorkflowResult, SystemOverview, LearningAnalytics
from ml.data.providers.dataset_manager import DatasetManager


class MLIntegration:
    """
    Тонкая прослойка между веб-интерфейсом и WorkflowManager
    """
    
    def __init__(self, config_path: str = None):
        self.project_root = project_root
        self.orchestrator = None
        self.is_initialized = False
        self.config_path = config_path or os.path.join(project_root, 'config', 'orchestrator_config.yaml')
        self.logger = logging.getLogger(__name__)
        
    def initialize(self) -> bool:
        """Инициализация ML системы с загрузкой сохраненной модели"""
        try:
            self.logger.info("🔄 Инициализация ML системы...")
            
            # Загружаем конфигурацию
            config = self._load_config()
            
            # Создаем оркестратор
            self.orchestrator = MLOrchestrator(config)
            
            # 🔧 ИСПРАВЛЕНИЕ: Пытаемся загрузить сохраненную модель
            model_loaded = self._load_saved_model()
            
            if not model_loaded:
                self.logger.info("🔄 Сохраненная модель не найдена, используем новую модель")
            
            self.logger.info(f"✅ Зарегистрированные модели: {list(self.orchestrator.models.keys())}")
            
            # Инициализируем компоненты
            self._initialize_components()
            
            self.is_initialized = True
            self.logger.info("✅ ML система успешно инициализирована")
            return True
            
        except Exception as e:
            self.logger.error(f"❌ Ошибка инициализации ML системы: {e}")
            self.is_initialized = False
            return False
 
    def _load_saved_model(self) -> bool:
        """Загрузка сохраненной модели - УПРОЩЕННАЯ ИСПРАВЛЕННАЯ ВЕРСИЯ"""
        try:
            model_path = os.path.join(self.project_root, 'data', 'models', 'enhanced_predictor_v2.pth')
            
            if not os.path.exists(model_path):
                self.logger.info("📭 Файл модели не найден, будет создана новая модель")
                return False
            
            self.logger.info(f"🔍 Найден файл модели: {model_path}")
            
            # 🔧 ИСПРАВЛЕНИЕ: Простая загрузка через ModelManager без сложной логики
            from ml.models.base import EnhancedPredictor
            
            success = self.orchestrator.model_manager.load_model(
                "enhanced_predictor_v2", 
                model_path, 
                EnhancedPredictor
            )
            
            if success:
                # 🔧 ПРОСТАЯ ПРОВЕРКА: Убеждаемся, что модель в оркестраторе
                model = self.orchestrator.models.get("enhanced_predictor_v2")
                if model:
                    self.logger.info(f"✅ Модель загружена и готова: обучена={model.is_trained}")
                    return True
                else:
                    self.logger.error("❌ Модель не найдена в оркестраторе после загрузки")
                    return False
            else:
                self.logger.error("❌ Не удалось загрузить модель через ModelManager")
                return False
                
        except Exception as e:
            self.logger.error(f"❌ Ошибка загрузки сохраненной модели: {e}")
            return False
   
    def _load_config(self) -> Dict[str, Any]:
        """Загрузка конфигурации"""
        try:
            import yaml
            with open(self.config_path, 'r', encoding='utf-8') as f:
                return yaml.safe_load(f)
        except Exception as e:
            self.logger.warning(f"⚠️ Не удалось загрузить конфигурацию: {e}")
            return {}
    
    def _initialize_components(self):
        """Инициализация компонентов системы"""
        # Создаем необходимые директории
        directories = [
            os.path.join(self.project_root, 'data', 'models'),
            os.path.join(self.project_root, 'data', 'datasets'), 
            os.path.join(self.project_root, 'data', 'analytics'),
            os.path.join(self.project_root, 'data', 'debug')  # 🔧 ДОБАВЛЕНО: для отладки
        ]
        
        for directory in directories:
            os.makedirs(directory, exist_ok=True)
            self.logger.debug(f"📁 Создана директория: {directory}")
        
    def get_system_status(self) -> Dict[str, Any]:
        if not self.is_initialized or not self.orchestrator:
            return {
                'is_initialized': False,
                'is_trained': False,
                'dataset_size': 0,
                'has_sufficient_data': False,
                'architecture': 'НОВАЯ МОДУЛЬНАЯ',
                'model_type': 'УСИЛЕННАЯ НЕЙРОСЕТЬ',
                'model_loaded': False
            }
        
        try:
            # Проверяем наличие сохраненной модели
            model_path = os.path.join(self.project_root, 'data', 'models', 'enhanced_predictor_v2.pth')
            model_file_exists = os.path.exists(model_path)
            
            # 🔧 КРИТИЧЕСКОЕ ИСПРАВЛЕНИЕ: Проверяем реальный статус модели, а не историю обучения
            model_loaded = False
            model_info = {}
            
            if "enhanced_predictor_v2" in self.orchestrator.models:
                model = self.orchestrator.models["enhanced_predictor_v2"]
                model_loaded = model.is_trained  # 🔧 ИСПОЛЬЗУЕМ РЕАЛЬНЫЙ СТАТУС МОДЕЛИ
                model_info = {
                    'is_trained': model.is_trained,
                    'status': model.status.value,
                    'input_size': getattr(model, 'input_size', 'unknown'),
                    'model_loaded_from_file': model_file_exists
                }
            
            # Получаем обзор системы
            overview = self.orchestrator.get_system_overview()
            
            # Загружаем данные для дополнительной информации
            dataset_manager = DatasetManager()
            dataset = dataset_manager.load_dataset()
            
            return {
                'is_initialized': True,
                'is_trained': model_loaded,  # 🔧 ИСПОЛЬЗУЕМ РЕАЛЬНЫЙ СТАТУС, а не overview.training_status
                'dataset_size': len(dataset),
                'has_sufficient_data': len(dataset) >= 50,
                'architecture': 'НОВАЯ МОДУЛЬНАЯ',
                'model_type': 'УСИЛЕННАЯ НЕЙРОСЕТЬ',
                'model_loaded': model_loaded,
                'model_info': model_info,
                'system_overview': overview.model_dump(),
                'registered_models': list(self.orchestrator.models.keys())
            }
        except Exception as e:
            self.logger.error(f"❌ Ошибка получения статуса системы: {e}")
            return {
                'is_initialized': True,
                'is_trained': False,
                'dataset_size': 0,
                'has_sufficient_data': False,
                'architecture': 'НОВАЯ МОДУЛЬНАЯ',
                'model_type': 'УСИЛЕННАЯ НЕЙРОСЕТЬ',
                'model_loaded': False,
                'error': str(e)
            }
      
    def run_full_training(self) -> WorkflowResult:
        """Запуск полного обучения"""
        if not self.is_initialized or not self.orchestrator:
            raise RuntimeError("Система не инициализирована")
        
        print("🎯 ВЫЗВАН: MLIntegration.run_full_training()")
        print(f"🎯 Orchestrator: {self.orchestrator}")
        print(f"🎯 Зарегистрированные модели: {list(self.orchestrator.models.keys())}")
    
        if hasattr(self.orchestrator, 'workflow_full_training_cycle'):
            print("✅ Orchestrator ИМЕЕТ метод workflow_full_training_cycle")
        else:
            print("❌ Orchestrator НЕ ИМЕЕТ метод workflow_full_training_cycle")
            print(f"🎯 Доступные методы: {[m for m in dir(self.orchestrator) if not m.startswith('_')]}")
        
        self.logger.info("🎯 Запуск полного обучения через WorkflowManager")
        return self.orchestrator.workflow_full_training_cycle()
    
    def generate_predictions(self) -> WorkflowResult:
        """Генерация прогнозов"""
        if not self.is_initialized or not self.orchestrator:
            raise RuntimeError("Система не инициализирована")
        
        self.logger.info("🎯 Запуск генерации прогнозов через WorkflowManager")
        return self.orchestrator.workflow_generate_predictions()
    
    def add_single_group(self, group: List[int]) -> WorkflowResult:
        """Добавление одной группы"""
        if not self.is_initialized or not self.orchestrator:
            raise RuntimeError("Система не инициализирована")
        
        self.logger.info(f"🎯 Добавление одной группы через WorkflowManager: {group}")
        return self.orchestrator.workflow_add_single_group(group)
    
    def add_multiple_groups(self, groups: List[List[int]], strategy: str = "full_retrain") -> WorkflowResult:
        """Добавление нескольких групп"""
        if not self.is_initialized or not self.orchestrator:
            raise RuntimeError("Система не инициализирована")
        
        self.logger.info(f"🎯 Добавление {len(groups)} групп через WorkflowManager (стратегия: {strategy})")
        return self.orchestrator.workflow_add_multiple_groups(groups, strategy)
    
    def get_learning_insights(self) -> Dict[str, Any]:
        """Получение аналитики обучения"""
        if not self.is_initialized or not self.orchestrator:
            return {'message': 'Система не инициализирована'}
        
        try:
            analytics = self.orchestrator.get_learning_analytics()
            return analytics.model_dump()
        except Exception as e:
            self.logger.error(f"❌ Ошибка получения аналитики: {e}")
            return {'error': str(e)}
