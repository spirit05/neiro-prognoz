# /opt/model/ml/ensemble/__init__.py
"""
Ансамблевые методы для комбинирования предсказаний - ЧИСТАЯ АРХИТЕКТУРА
"""

from .base_ensemble import AbstractEnsemblePredictor, WeightedEnsemblePredictor
from .predictors.statistical import StatisticalPredictor
from .predictors.pattern_based import PatternBasedPredictor
from .predictors.frequency import FrequencyPredictor
from .combiners.weighted_combiner import WeightedCombiner
from .factory import EnsembleFactory

__all__ = [
    'AbstractEnsemblePredictor',
    'WeightedEnsemblePredictor',
    'StatisticalPredictor',
    'PatternBasedPredictor', 
    'FrequencyPredictor',
    'WeightedCombiner',
    'EnsembleFactory'
]
