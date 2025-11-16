# /opt/model/ml/learning/analyzers/__init__.py
"""
Пакет анализаторов для системы самообучения
"""

from .performance import PerformanceAnalyzer
from .error_patterns import ErrorPatternAnalyzer

__all__ = ['PerformanceAnalyzer', 'ErrorPatternAnalyzer']
