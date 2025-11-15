"""
Стратегии обучения
"""
from .basic_training import BasicTrainingStrategy
from .incremental import IncrementalTrainingStrategy

__all__ = ['BasicTrainingStrategy', 'IncrementalTrainingStrategy']
