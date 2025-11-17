# [file name]: ml/core/__init__.py
"""
Пакет core новой архитектуры ML системы - ЧИСТАЯ АРХИТЕКТУРА
"""
from .base_model import AbstractBaseModel, AbstractDataProcessor
from .orchestrator import MLOrchestrator
from .config_loader import ConfigLoader
from .types import (
    ModelType, ModelStatus, TrainingConfig, ModelMetadata,
    TrainingResult, PredictionResponse, DataBatch, FeatureSpec,
    PredictionRequest, DataType, AnalysisResult, LearningHistory
)

__all__ = [
    'AbstractBaseModel',
    'AbstractDataProcessor', 
    'MLOrchestrator',
    'ConfigLoader',
    'ModelType',
    'ModelStatus',
    'TrainingConfig',
    'ModelMetadata',
    'TrainingResult',
    'PredictionResponse',
    'PredictionRequest',
    'DataBatch',
    'FeatureSpec',
    'DataType',
    'AnalysisResult',
    'LearningHistory'
]
