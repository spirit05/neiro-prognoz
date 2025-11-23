# [file name]: ml/__init__.py
"""
ML System Package
"""

__version__ = "1.0.0"
__author__ = "AI Prediction System"

# Импорты для удобства
try:
    from .core import MLOrchestrator, AbstractBaseModel
    from .ensemble import WeightedEnsemblePredictor
    from .features.engineers import StatisticalEngineer, AdvancedEngineer
    from .data.processors import ModularDataProcessor
    from .data.providers import DatasetManager
except ImportError:
    # Игнорируем ошибки импорта при установке
    pass

__all__ = [
    'MLOrchestrator',
    'AbstractBaseModel', 
    'WeightedEnsemblePredictor',
    'StatisticalEngineer',
    'AdvancedEngineer',
    'ModularDataProcessor',
    'DatasetManager'
]
