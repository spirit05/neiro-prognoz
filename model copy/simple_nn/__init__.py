# model/simple_nn/__init__.py
from .model import EnhancedNumberPredictor
from .predictor import EnhancedPredictor
from .trainer import EnhancedTrainer
from .features import FeatureExtractor
from .data_processor import DataProcessor

# Для обратной совместимости
SimpleNumberPredictor = EnhancedNumberPredictor
SimplePredictor = EnhancedPredictor
SimpleTrainer = EnhancedTrainer