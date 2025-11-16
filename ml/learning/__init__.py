# /opt/model/ml/learning/__init__.py
"""
Пакет системы самообучения - ЭТАП 6
"""

from .self_learning import SelfLearningSystem
from .analyzers.performance import PerformanceAnalyzer
from .analyzers.error_patterns import ErrorPatternAnalyzer

__all__ = [
    'SelfLearningSystem',
    'PerformanceAnalyzer',
    'ErrorPatternAnalyzer'
]
