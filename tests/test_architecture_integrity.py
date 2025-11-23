# [file name]: tests/test_architecture_integrity.py
"""
Тест структуры модулей - ОБНОВЛЕН С ПРАВИЛЬНОЙ НАСТРОЙКОЙ ПУТЕЙ
"""

import pytest
from pathlib import Path
import importlib
import sys
import os


# 🔧 ДОБАВЛЕНО: Правильная настройка путей для импортов
def setup_module():
    """Настройка путей перед запуском тестов"""
    project_root = Path(__file__).parent.parent
    sys.path.insert(0, str(project_root))
    
    # Также добавляем путь к ml директории на всякий случай
    ml_path = project_root / "ml"
    if ml_path.exists():
        sys.path.insert(0, str(ml_path))


def test_module_structure():
    """Тест структуры модулей на основе реальной структуры проекта"""
    setup_module()  # 🔧 ДОБАВЛЕНО: Настраиваем пути
    
    base_dir = Path(__file__).parent.parent
    
    # 🔧 ОБНОВЛЕНО: Реальный список файлов из структуры проекта
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
        "ml/ensemble/factory.py",
        "ml/ensemble/combiners/__init__.py",
        "ml/ensemble/combiners/weighted_combiner.py",
        "ml/ensemble/predictors/__init__.py",
        "ml/ensemble/predictors/frequency.py",
        "ml/ensemble/predictors/pattern_based.py",
        "ml/ensemble/predictors/statistical.py",
        
        # Data processing (Этап 8)
        "ml/data/__init__.py",
        "ml/data/processors/__init__.py",
        "ml/data/processors/data_processor.py",
        "ml/data/providers/__init__.py",
        "ml/data/providers/dataset_manager.py",
        "ml/data/quality/__init__.py",
        "ml/data/quality/validators.py",
        
        # Features (актуальная структура)
        "ml/features/__init__.py",
        "ml/features/base.py",
        "ml/features/engineers/__init__.py",
        "ml/features/engineers/advanced.py",
        "ml/features/engineers/statistical.py",
        "ml/features/selectors/__init__.py",
        "ml/features/transformers/__init__.py",
        
        # Learning
        "ml/learning/__init__.py",
        "ml/learning/self_learning.py",
        "ml/learning/analyzers/__init__.py",
        "ml/learning/analyzers/error_patterns.py",
        "ml/learning/analyzers/performance.py",
        
        # Models
        "ml/models/__init__.py",
        "ml/models/base/__init__.py",
        "ml/models/base/enhanced_predictor.py",
        
        # Training
        "ml/training/__init__.py",
        "ml/training/strategies/__init__.py",
        "ml/training/strategies/basic_training.py",
        "ml/training/strategies/incremental.py",
        "ml/training/optimizers/__init__.py",
        "ml/training/optimizers/enhanced_optimizer.py",
        
        # Конфигурация
        "config/__init__.py",
        "config/ensemble_config.yaml",
        "config/feature_config.yaml",
        "config/learning_config.yaml",
        "config/model_config.yaml",
        "config/orchestrator_config.yaml",
        
        # Приложение
        "app/__init__.py",
        "app/main.py",
        
        # Тесты
        "tests/__init__.py",
        "tests/conftest.py",
    ]
    
    missing_files = []
    for file_path in key_files:
        full_path = base_dir / file_path
        if not full_path.exists():
            missing_files.append(str(full_path))
    
    # 🔧 ОБНОВЛЕНО: Выводим информацию об отсутствующих файлах
    if missing_files:
        print("⚠️ Отсутствующие файлы:")
        for file in missing_files:
            print(f"   - {file}")
    
    assert len(missing_files) == 0, f"Отсутствующие файлы: {missing_files}"
    
    print("✅ Структура модулей соответствует актуальной архитектуре")


def test_core_imports():
    """Тест импортов core модулей"""
    setup_module()  # 🔧 ДОБАВЛЕНО: Настраиваем пути
    
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
        
        # Features (актуальные импорты)
        from ml.features.engineers import StatisticalEngineer, AdvancedEngineer
        
        print("✅ Все основные импорты работают")
        
    except ImportError as e:
        pytest.fail(f"Ошибка импорта: {e}")


def test_orchestrator_backward_compatibility():
    """Тест обратной совместимости оркестратора"""
    setup_module()  # 🔧 ДОБАВЛЕНО: Настраиваем пути
    
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
    setup_module()  # 🔧 ДОБАВЛЕНО: Настраиваем пути
    
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


def test_feature_engineers_availability():
    """Тест доступности feature engineers"""
    setup_module()  # 🔧 ДОБАВЛЕНО: Настраиваем пути
    
    try:
        from ml.features.engineers import StatisticalEngineer, AdvancedEngineer
        
        # Проверяем создание инженеров
        stat_engineer = StatisticalEngineer(history_size=20)
        adv_engineer = AdvancedEngineer(history_size=20)
        
        assert stat_engineer is not None, "StatisticalEngineer не создан"
        assert adv_engineer is not None, "AdvancedEngineer не создан"
        
        print("✅ Feature engineers доступны и работают")
        
    except Exception as e:
        pytest.fail(f"Ошибка feature engineers: {e}")


def test_old_monolithic_orchestrator_removed():
    """Тест что старый монолитный orchestrator.py удален"""
    setup_module()  # 🔧 ДОБАВЛЕНО: Настраиваем пути
    
    base_dir = Path(__file__).parent.parent
    old_orchestrator_path = base_dir / "ml" / "core" / "orchestrator.py"
    
    # 🔧 ОБНОВЛЕНО: Проверяем что есть только файл для обратной совместимости
    # или что старый файл удален
    if old_orchestrator_path.exists():
        # Если файл существует, проверяем что это фасад для обратной совместимости
        with open(old_orchestrator_path, 'r') as f:
            content = f.read()
            assert "обратной совместимости" in content or "backward compatibility" in content, \
                "Старый orchestrator.py не был заменен фасадом"
        print("✅ Старый orchestrator.py заменен фасадом обратной совместимости")
    else:
        print("✅ Старый монолитный orchestrator.py удален")


def test_data_processing_components():
    """Тест компонентов обработки данных (Этап 8)"""
    setup_module()  # 🔧 ДОБАВЛЕНО: Настраиваем пути
    
    try:
        from ml.data.processors import ModularDataProcessor
        from ml.data.providers import DatasetManager
        from ml.data.quality.validators import DataValidator
        
        # Проверяем создание компонентов
        processor = ModularDataProcessor()
        dataset_manager = DatasetManager()
        validator = DataValidator()
        
        assert processor is not None, "ModularDataProcessor не создан"
        assert dataset_manager is not None, "DatasetManager не создан" 
        assert validator is not None, "DataValidator не создан"
        
        print("✅ Компоненты обработки данных (Этап 8) работают")
        
    except Exception as e:
        pytest.fail(f"Ошибка компонентов обработки данных: {e}")


if __name__ == "__main__":
    # 🔧 ДОБАВЛЕНО: Настраиваем пути при запуске напрямую
    setup_module()
    
    # Запуск тестов вручную
    test_module_structure()
    test_core_imports() 
    test_orchestrator_backward_compatibility()
    test_workflow_manager_availability()
    test_feature_engineers_availability()
    test_old_monolithic_orchestrator_removed()
    test_data_processing_components()
    print("🎉 Все тесты архитектуры пройдены!")
