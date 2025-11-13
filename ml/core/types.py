"""
Базовые типы данных для ML системы
"""
from typing import Dict, List, Optional, Union, Any
from pydantic import BaseModel, Field, ConfigDict
from enum import Enum
import pandas as pd
import numpy as np
from datetime import datetime


class ModelType(str, Enum):
    """Типы моделей"""
    REGRESSION = "regression"
    CLASSIFICATION = "classification" 
    TIMESERIES = "timeseries"
    ANOMALY_DETECTION = "anomaly_detection"


class DataType(str, Enum):
    """Типы данных"""
    TRAINING = "training"
    VALIDATION = "validation" 
    TESTING = "testing"
    PREDICTION = "prediction"


class ModelStatus(str, Enum):
    """Статусы модели"""
    TRAINING = "training"
    TRAINED = "trained"
    EVALUATING = "evaluating"
    READY = "ready"
    FAILED = "failed"


class TrainingConfig(BaseModel):
    """Конфигурация обучения"""
    batch_size: int = Field(default=32, ge=1)
    learning_rate: float = Field(default=0.001, gt=0.0)
    epochs: int = Field(default=100, ge=1)
    early_stopping_patience: int = Field(default=10, ge=1)
    validation_split: float = Field(default=0.2, gt=0.0, lt=1.0)


class ModelMetadata(BaseModel):
    """Метаданные модели"""
    model_id: str
    model_type: ModelType
    version: str = "1.0.0"
    created_at: datetime = Field(default_factory=datetime.now)
    updated_at: datetime = Field(default_factory=datetime.now)
    features: List[str] = Field(default_factory=list)
    target_columns: List[str] = Field(default_factory=list)
    performance_metrics: Dict[str, float] = Field(default_factory=dict)


class TrainingResult(BaseModel):
    """Результат обучения"""
    model_id: str
    status: ModelStatus
    training_loss: List[float] = Field(default_factory=list)
    validation_loss: List[float] = Field(default_factory=list)
    metrics: Dict[str, float] = Field(default_factory=dict)
    training_time: float = 0.0
    best_epoch: int = 0


class PredictionRequest(BaseModel):
    """Запрос на предсказание"""
    data: Union[List[Dict[str, Any]], Dict[str, List[Any]]]
    model_id: str
    return_probabilities: bool = False
    batch_size: Optional[int] = None


class PredictionResponse(BaseModel):
    """Ответ с предсказаниями"""
    predictions: Union[List[float], List[int], List[str]]
    probabilities: Optional[List[List[float]]] = None
    model_id: str
    inference_time: float
    timestamp: datetime = Field(default_factory=datetime.now)


class DataBatch(BaseModel):
    """Пакет данных"""
    model_config = ConfigDict(arbitrary_types_allowed=True)
    
    data: pd.DataFrame
    batch_id: str
    data_type: DataType
    metadata: Dict[str, Any] = Field(default_factory=dict)


class FeatureSpec(BaseModel):
    """Спецификация фичи"""
    name: str
    dtype: str
    required: bool = True
    min_value: Optional[float] = None
    max_value: Optional[float] = None
    allowed_categories: Optional[List[str]] = None
