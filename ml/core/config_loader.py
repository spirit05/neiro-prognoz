# [file name]: ml/core/config_loader.py
"""
Загрузчик конфигурации для оркестратора - ИСПРАВЛЕННАЯ ВЕРСИЯ
"""

import yaml
import importlib
from pathlib import Path
from typing import Dict, Any
import logging

logger = logging.getLogger(__name__)

class ConfigLoader:
    """Загрузчик конфигурации YAML файлов - ИСПРАВЛЕННАЯ ВЕРСИЯ"""
    
    def __init__(self, config_dir: str = "/opt/model/config"):
        self.config_dir = Path(config_dir)
        logger.info(f"🔧 ConfigLoader инициализирован с директорией: {self.config_dir}")
    
    def load_yaml_config(self, config_name: str) -> Dict[str, Any]:
        """Загрузка конфигурации из YAML файла - ИСПРАВЛЕННАЯ ВЕРСИЯ"""
        config_path = self.config_dir / f"{config_name}.yaml"
        
        logger.info(f"📁 Попытка загрузки конфигурации: {config_path}")
        
        if not config_path.exists():
            logger.error(f"❌ Config file not found: {config_path}")
            return {}
        
        try:
            with open(config_path, 'r', encoding='utf-8') as f:
                config_data = yaml.safe_load(f)
            
            logger.info(f"✅ Конфигурация загружена: {config_name}")
            return config_data or {}
            
        except Exception as e:
            logger.error(f"❌ Ошибка загрузки конфигурации {config_name}: {e}")
            return {}
    
    def load_component_configs(self) -> Dict[str, Any]:
        """Загрузка всех конфигураций компонентов - ИСПРАВЛЕННАЯ ВЕРСИЯ"""
        configs = {}
        
        logger.info("🔄 Загрузка всех конфигураций компонентов...")
        
        # Основная конфигурация модели
        model_config = self.load_yaml_config('model_config')
        configs['model'] = model_config.get('model', {}) if model_config else {}
        
        # Конфигурация ансамбля
        ensemble_config = self.load_yaml_config('ensemble_config')
        configs['ensemble'] = ensemble_config.get('ensemble', {}) if ensemble_config else {}
        
        # Конфигурация обучения
        learning_config = self.load_yaml_config('learning_config')
        configs['learning'] = learning_config.get('learning', {}) if learning_config else {}
        
        # Конфигурация фич
        feature_config = self.load_yaml_config('feature_config')
        configs['features'] = feature_config if feature_config else {}
        
        logger.info("✅ Все конфигурации компонентов загружены")
        logger.info(f"📊 Статистика: model={bool(configs['model'])}, ensemble={bool(configs['ensemble'])}, learning={bool(configs['learning'])}, features={bool(configs['features'])}")
        
        return configs
    
    def dynamic_import(self, class_path: str) -> Any:
        """Динамический импорт класса по пути - ИСПРАВЛЕННАЯ ВЕРСИЯ"""
        try:
            logger.info(f"🔄 Динамический импорт: {class_path}")
            module_path, class_name = class_path.rsplit('.', 1)
            module = importlib.import_module(module_path)
            class_obj = getattr(module, class_name)
            logger.info(f"✅ Класс загружен: {class_path}")
            return class_obj
        except Exception as e:
            logger.error(f"❌ Ошибка импорта класса {class_path}: {e}")
            return None
    
    def create_component(self, class_path: str, params: Dict[str, Any]) -> Any:
        """Создание экземпляра компонента - ИСПРАВЛЕННАЯ ВЕРСИЯ"""
        try:
            component_class = self.dynamic_import(class_path)
            if component_class is None:
                logger.error(f"❌ Не удалось загрузить класс: {class_path}")
                return None
            
            logger.info(f"🔄 Создание компонента {class_path} с параметрами: {params}")
            instance = component_class(**params)
            logger.info(f"✅ Компонент создан: {class_path}")
            return instance
            
        except Exception as e:
            logger.error(f"❌ Ошибка создания компонента {class_path}: {e}")
            return None
