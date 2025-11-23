# [file name]: tests/test_architecture_integrity.py
# ИСПРАВЛЕННАЯ ВЕРСИЯ - обновлена для модульной архитектуры

import pytest
from pathlib import Path
import importlib
import sys


def test_module_structure():
    """Тест структуры модулей - ОБНОВЛЕН ДЛЯ МОДУЛЬНОЙ АРХИТЕКТУРЫ"""
    base_dir = Path(__file__).parent.parent
    
    # 🔧 ОБНОВЛЕНО: Заменяем старый монолитный файл на новую модульную структуру
    key_files = [
        # Основные core файлы
        "ml/core/__init__.py",
        "ml/core/base_model.py", 
        "ml/core/types.py",
        "ml/core/config_loader.py",
        
        # 🔧 НОВАЯ МОДУЛЬНАЯ СТРУКТУРА ORCHESTRATOR
        "ml/core/orchestrator/__init__.py",
        "ml/core/orchestrator/base_orchestrator.py",
        "ml/core/orchestrator/managers/__init__.py",
        "ml/core/orchestrator/managers/model_manager.py",
        "ml/core/orchestrator/managers/data_manager.py", 
        "ml/core/orchestrator/managers/workflow_manager.py",
        "ml/core/orchestrator/managers/notification_manager.py",
        "ml/core/orchestrator/managers/api_manager.py",
        "ml/core/orchestrator/types/__init__.py",
        "ml/core/orchestrator/types/workflow_types.py",
        
        # Ансамблевые системы
        "ml/ensemble/__init__.py",
        "ml/ensemble/base_ensemble.py",
        
        # Data processing (Этап 8)
        "ml/data/processors/data_processor.py",
        "ml/data/providers/dataset_manager.py",
        "ml/data/quality/validators.py",
        
        # Features
        "ml/features/__init__.py", 
        "ml/features/base.py",
        "ml/features/engineers.py",
        
        # Utils
        "ml/utils/__init__.py",
        "ml/utils/data_utils.py",
    ]
    
    missing_files = []
    for file_path in key_files:
        full_path = base_dir / file_path
        if not full_path.exists():
            missing_files.append(str(full_path))
    
    # 🔧 ОБНОВЛЕНО: Убираем старый orchestrator.py из проверки
    assert len(missing_files) == 0, f"Отсутствующие файлы: {missing_files}"
    
    print("✅ Структура модулей соответствует новой архитектуре")


def test_core_imports():
    """Тест импортов core модулей"""
    try:
        # Основные core импорты
        from ml.core import MLOrchestrator, AbstractBaseModel
        from ml.core.types import ModelType, ModelStatus, DataBatch
        
        # 🔧 ОБНОВЛЕНО: Импорты из новой модульной структуры
        from ml.core.orchestrator import MLOrchestrator as ModularOrchestrator
        from ml.core.orchestrator.managers import ModelManager, DataManager, WorkflowManager
        
        # Ансамблевые системы
        from ml.ensemble import WeightedEnsemblePredictor
        
        # Data processing
        from ml.data.processors import ModularDataProcessor
        from ml.data.providers import DatasetManager
        
        print("✅ Все основные импорты работают")
        
    except ImportError as e:
        pytest.fail(f"Ошибка импорта: {e}")


def test_orchestrator_backward_compatibility():
    """Тест обратной совместимости оркестратора"""
    try:
        # Старый импорт должен работать
        from ml.core.orchestrator import MLOrchestrator
        
        orchestrator = MLOrchestrator()
        
        # 🔧 ОБНОВЛЕНО: Проверяем что это действительно модульная версия
        assert hasattr(orchestrator, 'model_manager'), "Модульный оркестратор не загружен"
        assert hasattr(orchestrator, 'workflow_manager'), "WorkflowManager не доступен"
        
        # Проверяем обратную совместимость методов
        required_methods = [
            'register_model', 'train_model', 'predict', 'get_model_info',
            'list_models', 'prepare_training_data', 'get_system_status'
        ]
        
        for method in required_methods:
            assert hasattr(orchestrator, method), f"Метод {method} отсутствует"
            
        print("✅ Обратная совместимость оркестратора обеспечена")
        
    except Exception as e:
        pytest.fail(f"Ошибка обратной совместимости: {e}")


def test_workflow_manager_availability():
    """Тест доступности WorkflowManager (Этап 10)"""
    try:
        from ml.core.orchestrator import MLOrchestrator
        
        orchestrator = MLOrchestrator()
        
        # Проверяем новые workflow методы
        workflow_methods = [
            'workflow_add_single_group',
            'workflow_add_multiple_groups', 
            'workflow_full_training_cycle',
            'workflow_generate_predictions',
            'get_system_overview',
            'get_learning_analytics'
        ]
        
        for method in workflow_methods:
            assert hasattr(orchestrator, method), f"Workflow метод {method} отсутствует"
            
        print("✅ WorkflowManager готов для Этапа 10")
        
    except Exception as e:
        pytest.fail(f"Ошибка WorkflowManager: {e}")


# 🔧 ДОБАВЛЕНО: Тест для проверки что старый файл действительно удален
def test_old_monolithic_orchestrator_removed():
    """Тест что старый монолитный orchestrator.py удален"""
    base_dir = Path(__file__).parent.parent
    old_orchestrator_path = base_dir / "ml" / "core" / "orchestrator.py"
    
    # Ожидаем что старый файл удален
    assert not old_orchestrator_path.exists(), "Старый монолитный orchestrator.py все еще существует!"
    
    print("✅ Старый монолитный orchestrator.py успешно удален")


if __name__ == "__main__":
    # Запуск тестов вручную
    test_module_structure()
    test_core_imports() 
    test_orchestrator_backward_compatibility()
    test_workflow_manager_availability()
    test_old_monolithic_orchestrator_removed()
    print("🎉 Все тесты архитектуры пройдены!")
