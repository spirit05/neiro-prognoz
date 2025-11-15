# [file name]: tests/test_architecture_integrity.py
"""
Тесты архитектурной целостности новой ML системы
"""

import os
import pytest
import importlib
from pathlib import Path


def test_abstract_feature_engineer_interface():
    """Тест интерфейса AbstractFeatureEngineer"""
    # Проверяем, что класс существует и абстрактный
    from ml.features.base import AbstractFeatureEngineer
    import inspect
    
    # Проверяем, что класс абстрактный
    assert inspect.isabstract(AbstractFeatureEngineer)
    
    # Проверяем наличие абстрактных методов
    abstract_methods = AbstractFeatureEngineer.__abstractmethods__
    expected_methods = {'extract_features', 'get_feature_names'}
    assert abstract_methods == expected_methods
    
    # Проверяем, что нельзя создать экземпляр абстрактного класса
    try:
        engineer = AbstractFeatureEngineer(history_size=20)
        assert False, "Should not be able to instantiate abstract class"
    except TypeError:
        assert True  # Ожидаемое поведение


def test_module_structure():
    """Тест структуры модулей"""
    import ml
    
    # 🔧 ИСПРАВЛЕНИЕ: Используем правильные пути относительно корня проекта
    project_root = Path(__file__).parent.parent  # /opt/model
    
    # Проверяем существование основных модулей
    expected_modules = [
        'ml/core',
        'ml/models', 
        'ml/features',
        'ml/training',
        'ml/training/strategies',
        'ml/training/optimizers'
    ]
    
    for module_path in expected_modules:
        full_path = project_root / module_path
        assert full_path.exists(), f"Module path does not exist: {full_path}"
        assert (full_path / '__init__.py').exists(), f"Missing __init__.py in {full_path}"
    
    # Проверяем наличие ключевых файлов
    key_files = [
        'ml/core/base_model.py',
        'ml/core/orchestrator.py',
        'ml/core/types.py',
        'ml/models/base/enhanced_predictor.py',
        'ml/features/base.py',
        'ml/training/__init__.py',
        'ml/training/strategies/basic_training.py',
        'ml/training/strategies/incremental.py',
        'ml/training/optimizers/enhanced_optimizer.py'
    ]
    
    for file_path in key_files:
        full_path = project_root / file_path
        assert full_path.exists(), f"Key file does not exist: {full_path}"

def test_abstract_base_model_interface():
    """Тест интерфейса AbstractBaseModel"""
    from ml.core.base_model import AbstractBaseModel
    import inspect
    
    # Проверяем, что класс абстрактный
    assert inspect.isabstract(AbstractBaseModel)
    
    # Проверяем наличие абстрактных методов
    abstract_methods = AbstractBaseModel.__abstractmethods__
    expected_methods = {'train', 'predict', 'save', 'load'}
    assert abstract_methods == expected_methods


def test_ml_orchestrator_initialization():
    """Тест инициализации MLOrchestrator"""
    from ml.core.orchestrator import MLOrchestrator
    
    # Проверяем создание оркестратора
    orchestrator = MLOrchestrator({})
    assert orchestrator is not None
    assert hasattr(orchestrator, 'register_model')
    assert hasattr(orchestrator, 'train_model')
    assert hasattr(orchestrator, 'predict')


def test_enhanced_predictor_implementation():
    """Тест реализации EnhancedPredictor"""
    from ml.models.base.enhanced_predictor import EnhancedPredictor
    from ml.core.base_model import AbstractBaseModel
    
    # Проверяем, что класс наследует от AbstractBaseModel
    assert issubclass(EnhancedPredictor, AbstractBaseModel)
    
    # Проверяем создание экземпляра
    predictor = EnhancedPredictor("test_predictor")
    assert predictor is not None
    assert predictor.model_id == "test_predictor"


def test_training_strategies_availability():
    """Тест доступности стратегий обучения"""
    # Проверяем базовую стратегию
    from ml.training.strategies.basic_training import BasicTrainingStrategy
    basic_strategy = BasicTrainingStrategy()
    assert basic_strategy.strategy_id == "basic_training"
    
    # Проверяем инкрементальную стратегию
    from ml.training.strategies.incremental import IncrementalTrainingStrategy
    incremental_strategy = IncrementalTrainingStrategy()
    assert incremental_strategy.strategy_id == "incremental_training"


def test_feature_engineers_implementation():
    """Тест реализации feature engineers"""
    from ml.features.engineers.statistical import StatisticalEngineer
    from ml.features.engineers.advanced import AdvancedEngineer
    
    # Проверяем статистический инженер
    statistical_engineer = StatisticalEngineer()
    assert statistical_engineer is not None
    features = statistical_engineer.extract_features([1, 2, 3, 4, 5])
    assert len(features) == 50
    
    # Проверяем продвинутый инженер
    advanced_engineer = AdvancedEngineer()
    assert advanced_engineer is not None
    features = advanced_engineer.extract_features([1, 2, 3, 4, 5])
    assert len(features) == 15


def test_all_modules_can_be_imported():
    """Тест что все модули могут быть импортированы без ошибок"""
    modules_to_test = [
        'ml.core',
        'ml.core.base_model',
        'ml.core.orchestrator', 
        'ml.core.types',
        'ml.models.base',
        'ml.models.base.enhanced_predictor',
        'ml.features',
        'ml.features.base',
        'ml.features.engineers.statistical',
        'ml.features.engineers.advanced',
        'ml.training',
        'ml.training.strategies.basic_training',
        'ml.training.strategies.incremental',
        'ml.training.optimizers.enhanced_optimizer'
    ]
    
    for module_name in modules_to_test:
        try:
            importlib.import_module(module_name)
            assert True, f"Successfully imported {module_name}"
        except ImportError as e:
            assert False, f"Failed to import {module_name}: {e}"

def test_config_files_exist():
    """Тест наличия конфигурационных файлов"""
    # 🔧 ИСПРАВЛЕНИЕ: Используем правильные пути относительно корня проекта
    project_root = Path(__file__).parent.parent  # /opt/model
    
    config_files = [
        'config/model_config.yaml',
        'config/feature_config.yaml',
        'config/model_config.py',
        'config/feature_config.py'
    ]

    missing_files = []
    for config_file in config_files:
        full_path = project_root / config_file
        if not full_path.exists():
            missing_files.append(config_file)
    
    if missing_files:
        pytest.fail(f"Конфигурационные файлы отсутствуют: {missing_files}")
    else:
        assert True, "Все конфигурационные файлы присутствуют"

if __name__ == "__main__":
    pytest.main([__file__, "-v"])
