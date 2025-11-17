# [file name]: ml/data/__init__.py
"""
Модуль обработки данных для новой архитектуры
"""

from .processors.data_processor import ModularDataProcessor
from .providers.dataset_manager import DatasetManager
from .quality.validators import DataValidator

__all__ = ['ModularDataProcessor', 'DatasetManager', 'DataValidator']
