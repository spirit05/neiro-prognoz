# /opt/model/ml/core/__init__.py
"""
Пакет core новой архитектуры ML системы
"""
from .base_model import AbstractBaseModel, AbstractDataProcessor
from .orchestrator import MLOrchestrator
from .types import (
    ModelType, ModelStatus, TrainingConfig, ModelMetadata,
    TrainingResult, PredictionResponse, DataBatch, FeatureSpec,
    PredictionRequest, DataType, AnalysisResult, LearningHistory  # ✅ ДОБАВЛЕНО
)

__all__ = [
    'AbstractBaseModel',
    'AbstractDataProcessor', 
    'MLOrchestrator',
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
    'AnalysisResult',        # ✅ ДОБАВЛЕНО
    'LearningHistory'        # ✅ ДОБАВЛЕНО
]
