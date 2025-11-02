# [file name]: model/__init__.py
"""
Модели для предсказания чисел - УСИЛЕННАЯ ВЕРСИЯ с ансамблевыми методами и самообучением
"""

# Импорты для обратной совместимости
from .data_loader import load_dataset, save_dataset, validate_group, compare_groups, save_predictions, load_predictions

__version__ = "4.0.0"
__author__ = "AI Prediction System"
__description__ = "Усиленная система предсказания числовых последовательностей с ансамблевыми методами и самообучением"