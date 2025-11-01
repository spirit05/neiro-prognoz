# [file name]: model/__init__.py (ОБНОВЛЕННЫЙ)
"""
Модели для предсказания чисел - УСИЛЕННАЯ ВЕРСИЯ с ансамблевыми методами и самообучением
"""

# Импорты для обратной совместимости
from .data_loader import load_dataset, save_dataset, validate_group, compare_groups, save_predictions, load_predictions
from .simple_system import SimpleNeuralSystem

# НОВЫЕ импорты для расширенной функциональности
try:
    from .advanced_features import AdvancedPatternAnalyzer, FrequencyBasedPredictor, SmartNumberSelector
    from .ensemble_predictor import EnsemblePredictor, StatisticalPredictor, PatternBasedPredictor
    from .advanced_model import AdvancedSequencePredictor, CompatibleEnhancedPredictor
    from .self_learning import SelfLearningSystem
except ImportError as e:
    print(f"⚠️  Некоторые расширенные модули не загружены: {e}")

__version__ = "4.0.0"
__author__ = "AI Prediction System"
__description__ = "Усиленная система предсказания числовых последовательностей с ансамблевыми методами и самообучением"