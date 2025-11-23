# [file name]: ml/core/orchestrator/types/workflow_types.py
"""
Типы данных для WorkflowManager
"""

from typing import List, Dict, Any, Optional, Tuple
from pydantic import BaseModel, Field
from datetime import datetime
from enum import Enum


class WorkflowStatus(str, Enum):
    """Статусы workflow"""
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"


class WorkflowResult(BaseModel):
    """Результат выполнения workflow"""
    status: WorkflowStatus
    message: str
    data: Optional[Dict[str, Any]] = None
    error: Optional[str] = None
    timestamp: datetime = Field(default_factory=datetime.now)
    execution_time: float = 0.0
    steps_completed: List[str] = Field(default_factory=list)


class SystemOverview(BaseModel):
    """Комплексный обзор системы"""
    system_status: str
    model_status: str
    data_status: str
    training_status: str
    last_training: Optional[datetime] = None
    last_prediction: Optional[datetime] = None
    total_groups: int
    valid_groups: int
    model_metrics: Dict[str, Any] = Field(default_factory=dict)
    performance_metrics: Dict[str, Any] = Field(default_factory=dict)
    recommendations: List[str] = Field(default_factory=list)


class LearningAnalytics(BaseModel):
    """Аналитика обучения"""
    total_training_sessions: int
    recent_accuracy: float
    best_accuracy: float
    worst_accuracy: float
    average_training_time: float
    prediction_accuracy_trend: List[float] = Field(default_factory=list)
    feature_importance: Dict[str, float] = Field(default_factory=dict)
    model_performance: Dict[str, Any] = Field(default_factory=dict)
    learning_curves: Dict[str, List[float]] = Field(default_factory=dict)
