# [file name]: model/simple_nn/__init__.py (УПРОЩЕННЫЙ)
# model/simple_nn/__init__.py
from .model import EnhancedNumberPredictor
from .features import FeatureExtractor
from .data_processor import DataProcessor

# Для обратной совместимости #
SimpleNumberPredictor = EnhancedNumberPredictor