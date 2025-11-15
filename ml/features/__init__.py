# [file name]: ml/features/__init__.py
"""
Модульная система feature engineering для новой архитектуры
"""

from .base import AbstractFeatureEngineer
from .engineers.statistical import StatisticalEngineer
from .engineers.advanced import AdvancedEngineer

__all__ = [
    'AbstractFeatureEngineer',
    'StatisticalEngineer', 
    'AdvancedEngineer'
]
