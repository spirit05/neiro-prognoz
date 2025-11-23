# [file name]: tests/test_modular_orchestrator.py
"""
Тесты для модульного оркестратора
"""

import pytest
import sys
from pathlib import Path

# Добавляем корень проекта в путь
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from ml.core.orchestrator import MLOrchestrator
from ml.core.types import DataBatch, TrainingConfig, PredictionRequest
import pandas as pd
import numpy as np


def test_modular_orchestrator_initialization():
    """Тест инициализации модульного оркестратора"""
    orchestrator = MLOrchestrator()
    
    # Проверяем что менеджеры инициализированы
    assert hasattr(orchestrator, 'model_manager')
    assert hasattr(orchestrator, 'data_manager')
    assert hasattr(orchestrator, 'workflow_manager')
    assert hasattr(orchestrator, 'notification_manager')
    assert hasattr(orchestrator, 'api_manager')
    
    print("✅ Модульный оркестратор инициализирован корректно")


def test_backward_compatibility():
    """Тест обратной совместимости"""
    orchestrator = MLOrchestrator()
    
    # Проверяем что старые методы доступны
    assert hasattr(orchestrator, 'register_model')
    assert hasattr(orchestrator, 'train_model')
    assert hasattr(orchestrator, 'predict')
    assert hasattr(orchestrator, 'get_model_info')
    assert hasattr(orchestrator, 'list_models')
    assert hasattr(orchestrator, 'train_model_with_strategy')  # 🔧 ДОБАВЛЕННЫЙ МЕТОД
    assert hasattr(orchestrator, 'clear_registry')  # 🔧 ДОБАВЛЕННЫЙ МЕТОД
    
    print("✅ Обратная совместимость обеспечена")


def test_feature_engineers_initialization():
    """Тест инициализации feature engineers"""
    orchestrator = MLOrchestrator()
    
    # Проверяем что feature engineers загружены
    feature_engineers = orchestrator.get_feature_engineers()
    assert isinstance(feature_engineers, dict)
    assert len(feature_engineers) > 0, "Feature engineers не загружены"
    
    print(f"✅ Feature engineers загружены: {list(feature_engineers.keys())}")


def test_workflow_methods():
    """Тест новых workflow методов"""
    orchestrator = MLOrchestrator()
    
    # Проверяем что workflow методы доступны
    assert hasattr(orchestrator, 'workflow_add_single_group')
    assert hasattr(orchestrator, 'workflow_add_multiple_groups')
    assert hasattr(orchestrator, 'workflow_full_training_cycle')
    assert hasattr(orchestrator, 'workflow_generate_predictions')
    assert hasattr(orchestrator, 'get_system_overview')
    assert hasattr(orchestrator, 'get_learning_analytics')
    
    print("✅ Workflow методы доступны")


if __name__ == "__main__":
    print("🧪 Запуск тестов модульного оркестратора...")
    
    test_modular_orchestrator_initialization()
    test_backward_compatibility()
    test_feature_engineers_initialization() 
    test_workflow_methods()
    
    print("🎉 Все тесты модульного оркестратора пройдены!")
