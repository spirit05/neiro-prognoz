# /opt/model/ml/ensemble/predictors/__init__.py
"""
Predictors для ансамблевой системы - ПОЛНАЯ ФУНКЦИОНАЛЬНОСТЬ
"""

from .statistical import StatisticalPredictor
from .pattern_based import PatternBasedPredictor
from .frequency import FrequencyPredictor

__all__ = ['StatisticalPredictor', 'PatternBasedPredictor', 'FrequencyPredictor']
