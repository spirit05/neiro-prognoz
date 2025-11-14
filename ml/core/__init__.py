"""
Пакет core новой архитектуры ML системы
"""
from .base_model import AbstractBaseModel, AbstractDataProcessor
from .orchestrator import MLOrchestrator
from .types import (
    ModelType, ModelStatus, TrainingConfig, ModelMetadata,
    TrainingResult, PredictionResponse, DataBatch, FeatureSpec,
    PredictionRequest, DataType
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
    'DataType'
]
