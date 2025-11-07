# [file name]: tests/test_web_integration.py
"""
Тесты интеграции веб-сервиса с новой модульной архитектурой
"""

import sys
import os
import pytest
import tempfile
import json
from unittest.mock import Mock, patch, MagicMock

# Добавляем пути
sys.path.insert(0, '/opt/dev')
sys.path.insert(0, '/opt/dev/tests')

def test_ml_adapter_initialization():
    """Тест инициализации ML адаптера"""
    from web.components.ml_adapter import MLSystemAdapter
    
    # Создаем временные файлы для теста
    with tempfile.TemporaryDirectory() as temp_dir:
        with patch('web.components.ml_adapter.paths.MODEL_FILE', os.path.join(temp_dir, 'test_model.pth')):
            with patch('web.components.ml_adapter.paths.DATASET_FILE', os.path.join(temp_dir, 'test_dataset.json')):
                
                # Создаем mock для компонентов
                with patch('web.components.ml_adapter.EnhancedTrainer') as mock_trainer, \
                     patch('web.components.ml_adapter.EnhancedPredictor') as mock_predictor, \
                     patch('web.components.ml_adapter.SelfLearningSystem') as mock_learning:
                    
                    # Настраиваем mock'и
                    mock_predictor_instance = Mock()
                    mock_predictor_instance.load_model.return_value = True
                    mock_predictor.return_value = mock_predictor_instance
                    
                    # Создаем адаптер
                    adapter = MLSystemAdapter()
                    
                    # Проверяем инициализацию
                    assert adapter.is_trained == True
                    assert adapter.trainer is not None
                    assert adapter.predictor is not None
                    assert adapter.self_learning is not None
                    
                    print("✅ ML адаптер успешно инициализирован")

def test_ml_adapter_train_method():
    """Тест метода обучения адаптера"""
    from web.components.ml_adapter import MLSystemAdapter
    
    with tempfile.TemporaryDirectory() as temp_dir:
        # Создаем тестовый dataset
        test_dataset = ["1 2 3 4", "5 6 7 8", "9 10 11 12"] * 20  # 60 групп
        
        dataset_path = os.path.join(temp_dir, 'dataset.json')
        with open(dataset_path, 'w') as f:
            json.dump(test_dataset, f)
        
        with patch('web.components.ml_adapter.paths.DATASET_FILE', dataset_path), \
             patch('web.components.ml_adapter.paths.MODEL_FILE', os.path.join(temp_dir, 'model.pth')):
            
            with patch('web.components.ml_adapter.EnhancedTrainer') as mock_trainer_class, \
                 patch('web.components.ml_adapter.EnhancedPredictor') as mock_predictor_class:
                
                # Настраиваем mock тренера
                mock_trainer = Mock()
                mock_trainer.train.return_value = [((1, 2, 3, 4), 0.1), ((5, 6, 7, 8), 0.05)]
                mock_trainer_class.return_value = mock_trainer
                
                # Настраиваем mock предсказателя
                mock_predictor = Mock()
                mock_predictor.load_model.return_value = True
                mock_predictor_class.return_value = mock_predictor
                
                adapter = MLSystemAdapter()
                adapter.trainer = mock_trainer
                adapter.predictor = mock_predictor
                
                # Тестируем обучение
                predictions = adapter.train(epochs=10)
                
                # Проверяем результаты
                assert len(predictions) == 2
                assert predictions[0][0] == (1, 2, 3, 4)
                assert predictions[0][1] == 0.1
                assert adapter.is_trained == True
                
                print("✅ Метод обучения адаптера работает корректно")

def test_ml_adapter_predict_method():
    """Тест метода прогнозирования адаптера"""
    from web.components.ml_adapter import MLSystemAdapter
    
    with tempfile.TemporaryDirectory() as temp_dir:
        # Создаем тестовый dataset
        test_dataset = ["1 2 3 4", "5 6 7 8"] * 15  # 30 групп
        
        dataset_path = os.path.join(temp_dir, 'dataset.json')
        with open(dataset_path, 'w') as f:
            json.dump(test_dataset, f)
        
        with patch('web.components.ml_adapter.paths.DATASET_FILE', dataset_path):
            
            adapter = MLSystemAdapter()
            adapter.is_trained = True
            
            # Mock предсказателя
            mock_predictor = Mock()
            mock_predictor.predict_group.return_value = [((9, 10, 11, 12), 0.15), ((13, 14, 15, 16), 0.08)]
            adapter.predictor = mock_predictor
            
            # Тестируем прогнозирование
            predictions = adapter.predict(top_k=2)
            
            # Проверяем результаты
            assert len(predictions) == 2
            assert predictions[0][0] == (9, 10, 11, 12)
            assert mock_predictor.predict_group.called
            
            print("✅ Метод прогнозирования адаптера работает корректно")

def test_ml_adapter_add_data_method():
    """Тест метода добавления данных адаптера"""
    from web.components.ml_adapter import MLSystemAdapter
    from ml.utils.data_utils import save_dataset
    
    with tempfile.TemporaryDirectory() as temp_dir:
        # Создаем начальный dataset
        initial_dataset = ["1 2 3 4", "5 6 7 8"] * 25  # 50 групп
        
        dataset_path = os.path.join(temp_dir, 'dataset.json')
        save_dataset(initial_dataset)
        
        with patch('web.components.ml_adapter.paths.DATASET_FILE', dataset_path), \
             patch('web.components.ml_adapter.paths.MODEL_FILE', os.path.join(temp_dir, 'model.pth')):
            
            adapter = MLSystemAdapter()
            adapter.is_trained = True
            
            # Mock компонентов
            mock_trainer = Mock()
            mock_trainer.train.return_value = [((9, 10, 11, 12), 0.2)]
            adapter.trainer = mock_trainer
            
            mock_predictor = Mock()
            mock_predictor.load_model.return_value = True
            adapter.predictor = mock_predictor
            
            mock_learning = Mock()
            mock_learning.analyze_prediction_accuracy.return_value = {
                'accuracy_score': 0.5,
                'matches_count': 2
            }
            adapter.self_learning = mock_learning
            
            # Тестируем добавление данных
            new_sequence = "9 10 11 12"
            predictions = adapter.add_data_and_retrain(new_sequence, retrain_epochs=3)
            
            # Проверяем результаты
            assert len(predictions) == 1
            assert predictions[0][0] == (9, 10, 11, 12)
            assert mock_trainer.train.called
            assert mock_learning.analyze_prediction_accuracy.called
            
            print("✅ Метод добавления данных адаптера работает корректно")

def test_web_components_import():
    """Тест импорта всех веб-компонентов"""
    try:
        from web.components.ml_adapter import MLSystemAdapter, create_ml_system
        from web.components.sidebar import show_sidebar
        from web.components.training_ui import show_training_ui
        from web.components.prediction_ui import show_prediction_ui
        from web.components.data_ui import show_data_ui
        from web.components.status_ui import show_status_ui
        from web.components.utils import format_confidence_score, create_prediction_display
        from web.components.styles import apply_custom_styles
        
        print("✅ Все веб-компоненты успешно импортируются")
        
    except ImportError as e:
        pytest.fail(f"❌ Ошибка импорта веб-компонентов: {e}")

def test_utils_functions():
    """Тест вспомогательных функций"""
    from web.components.utils import (
        format_confidence_score,
        validate_and_format_group_input,
        get_system_status_badges
    )
    
    # Тест форматирования уверенности
    confidence_high, color_high = format_confidence_score(0.05)
    confidence_medium, color_medium = format_confidence_score(0.005)
    confidence_low, color_low = format_confidence_score(0.0001)
    
    assert "ВЫСОКАЯ" in confidence_high
    assert "СРЕДНЯЯ" in confidence_medium
    assert "НИЗКАЯ" in confidence_low
    
    # Тест валидации ввода
    is_valid, message = validate_and_format_group_input("1 2 3 4")
    assert is_valid == True
    assert "корректен" in message
    
    is_valid, message = validate_and_format_group_input("invalid input")
    assert is_valid == False
    assert "Неверный формат" in message
    
    # Тест бейджей статуса
    status = {
        'is_trained': True,
        'has_sufficient_data': True,
        'architecture': 'НОВАЯ МОДУЛЬНАЯ'
    }
    badges = get_system_status_badges(status)
    assert len(badges) == 3
    assert "Обучена" in badges[0]
    
    print("✅ Вспомогательные функции работают корректно")

def test_data_utils_integration():
    """Тест интеграции с утилитами данных"""
    from ml.utils.data_utils import (
        load_dataset,
        save_dataset,
        validate_group,
        compare_groups
    )
    
    with tempfile.TemporaryDirectory() as temp_dir:
        # Тестовые данные
        test_data = ["1 2 3 4", "5 6 7 8", "9 10 11 12"]
        
        # Тест сохранения и загрузки
        test_file = os.path.join(temp_dir, 'test_dataset.json')
        with patch('ml.utils.data_utils.paths.DATASET_FILE', test_file):
            save_dataset(test_data)
            loaded_data = load_dataset()
            
            assert loaded_data == test_data
            print("✅ Сохранение и загрузка dataset работают корректно")
        
        # Тест валидации групп
        assert validate_group("1 2 3 4") == True
        assert validate_group("1 1 3 4") == False  # Дубликаты в паре
        assert validate_group("1 2 3") == False    # Недостаточно чисел
        assert validate_group("1 2 3 27") == False # Число вне диапазона
        
        print("✅ Валидация групп работает корректно")
        
        # Тест сравнения групп
        group1 = (1, 2, 3, 4)
        group2 = (1, 5, 3, 6)
        comparison = compare_groups(group1, group2)
        
        assert comparison['total_matches'] == 2  # 1 и 3 совпадают
        assert comparison['pair1_matches'] == 1  # 1 совпадает в первой паре
        assert comparison['pair2_matches'] == 1  # 3 совпадает во второй паре
        
        print("✅ Сравнение групп работает корректно")

def test_ml_system_integration():
    """Тест интеграции с ML системой"""
    try:
        # Импорты из ML системы
        from ml.core.trainer import EnhancedTrainer
        from ml.core.predictor import EnhancedPredictor
        from ml.core.data_processor import DataProcessor
        from ml.learning.self_learning import SelfLearningSystem
        from ml.ensemble.ensemble import EnsemblePredictor
        
        print("✅ Все ML компоненты успешно импортируются")
        
    except ImportError as e:
        pytest.fail(f"❌ Ошибка импорта ML компонентов: {e}")

def test_config_integration():
    """Тест интеграции с конфигурацией"""
    from config import paths, constants, logging_config
    
    # Проверяем наличие основных путей
    assert hasattr(paths, 'PROJECT_ROOT')
    assert hasattr(paths, 'DATASET_FILE')
    assert hasattr(paths, 'MODEL_FILE')
    
    # Проверяем наличие основных констант
    assert hasattr(constants, 'MAIN_TRAINING_EPOCHS')
    assert hasattr(constants, 'PREDICTION_TOP_K')
    assert hasattr(constants, 'MIN_DATASET_SIZE')
    
    # Проверяем логирование
    logger = logging_config.get_ml_system_logger()
    assert logger is not None
    
    print("✅ Интеграция с конфигурацией работает корректно")

if __name__ == "__main__":
    # Запуск всех тестов
    print("🚀 ЗАПУСК ТЕСТОВ ВЕБ-СЕРВИСА...")
    
    test_ml_adapter_initialization()
    test_ml_adapter_train_method()
    test_ml_adapter_predict_method()
    test_ml_adapter_add_data_method()
    test_web_components_import()
    test_utils_functions()
    test_data_utils_integration()
    test_ml_system_integration()
    test_config_integration()
    
    print("🎉 ВСЕ ТЕСТЫ ПРОЙДЕНЫ УСПЕШНО!")