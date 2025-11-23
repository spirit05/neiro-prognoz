# [file name]: ml/core/orchestrator/types/__init__.py
"""
Типы данных для workflow
"""

from .workflow_types import (
    WorkflowStatus,
    WorkflowResult,
    SystemOverview, 
    LearningAnalytics
)

__all__ = [
    'WorkflowStatus',
    'WorkflowResult',
    'SystemOverview',
    'LearningAnalytics'
]
