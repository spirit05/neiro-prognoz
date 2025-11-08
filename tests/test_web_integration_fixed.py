# [file name]: tests/test_web_integration_fixed.py
"""
Исправленные тесты интеграции веб-сервиса
"""

import sys
import os
import tempfile
import json
from unittest.mock import Mock, patch, MagicMock
from pathlib import Path

sys.path.insert(0, '/opt/dev')

def test_ml_adapter_initialization():
    """Тест инициализации ML адаптера - ИСПРАВЛЕННАЯ ВЕРСИЯ"""
    print("🔍 ТЕСТ ИНИЦИАЛИЗАЦИИ ML АДАПТЕРА...")
    
    from web.components.ml_adapter import MLSystemAdapter
    
    # Создаем временные файлы для теста
    with tempfile.TemporaryDirectory() as temp_dir:
        temp_dir_path = Path(temp_dir)
        
        with patch('web.components.ml_adapter.paths.MODEL_FILE', temp_dir_path / 'test_model.pth'), \
             patch('web.components.ml_adapter.paths.DATASET_FILE', temp_dir_path / 'test_dataset.json'):
            
            # ⚡ ИСПРАВЛЕНИЕ: Патчим правильные модули
            with patch('ml.core.trainer.EnhancedTrainer') as mock_trainer_class, \
                 patch('ml.core.predictor.EnhancedPredictor') as mock_predictor_class, \
                 patch('ml.learning.self_learning.SelfLearningSystem') as mock_learning_class:
                
                # Настраиваем mock'и
                mock_predictor_instance = Mock()
                mock_predictor_instance.load_model.return_value = True
                mock_predictor_instance.is_trained = True
                mock_predictor_class.return_value = mock_predictor_instance
                
                # Создаем адаптер
                adapter = MLSystemAdapter()
                
                # Проверяем инициализацию
                assert adapter.is_trained == True
                assert adapter.trainer is not None
                assert adapter.predictor is not None
                assert adapter.self_learning is not None
                
                print("✅ ML адаптер успешно инициализирован")
                return True

def test_ml_adapter_train_method():
    """Тест метода обучения адаптера - ИСПРАВЛЕННАЯ ВЕРСИЯ"""
    print("🔍 ТЕСТ МЕТОДА ОБУЧЕНИЯ...")
    
    from web.components.ml_adapter import MLSystemAdapter
    
    with tempfile.TemporaryDirectory() as temp_dir:
        temp_dir_path = Path(temp_dir)
        
        # Создаем тестовый dataset
        test_dataset = ["1 2 3 4", "5 6 7 8", "9 10 11 12"] * 20  # 60 групп
        
        dataset_path = temp_dir_path / 'dataset.json'
        with open(dataset_path, 'w') as f:
            json.dump(test_dataset, f)
        
        with patch('web.components.ml_adapter.paths.DATASET_FILE', dataset_path), \
             patch('web.components.ml_adapter.paths.MODEL_FILE', temp_dir_path / 'model.pth'):
            
            # ⚡ ИСПРАВЛЕНИЕ: Патчим правильные модули
            with patch('ml.core.trainer.EnhancedTrainer') as mock_trainer_class, \
                 patch('ml.core.predictor.EnhancedPredictor') as mock_predictor_class:
                
                # Настраиваем mock тренера
                mock_trainer = Mock()
                mock_trainer.train.return_value = [((1, 2, 3, 4), 0.1), ((5, 6, 7, 8), 0.05)]
                mock_trainer_class.return_value = mock_trainer
                
                # Настраиваем mock предсказателя
                mock_predictor = Mock()
                mock_predictor.load_model.return_value = True
                mock_predictor.is_trained = True
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
                return True

def test_ml_adapter_predict_method():
    """Тест метода прогнозирования адаптера - ИСПРАВЛЕННАЯ ВЕРСИЯ"""
    print("🔍 ТЕСТ МЕТОДА ПРОГНОЗИРОВАНИЯ...")
    
    from web.components.ml_adapter import MLSystemAdapter
    
    with tempfile.TemporaryDirectory() as temp_dir:
        temp_dir_path = Path(temp_dir)
        
        # Создаем тестовый dataset
        test_dataset = ["1 2 3 4", "5 6 7 8"] * 15  # 30 групп
        
        dataset_path = temp_dir_path / 'dataset.json'
        with open(dataset_path, 'w') as f:
            json.dump(test_dataset, f)
        
        with patch('web.components.ml_adapter.paths.DATASET_FILE', dataset_path):
            
            adapter = MLSystemAdapter()
            adapter.is_trained = True
            
            # Mock предсказателя
            mock_predictor = Mock()
            mock_predictor.predict_group.return_value = [((9, 10, 11, 12), 0.15), ((13, 14, 15, 16), 0.08)]
            mock_predictor.is_trained = True
            adapter.predictor = mock_predictor
            
            # Тестируем прогнозирование
            predictions = adapter.predict(top_k=2)
            
            # Проверяем результаты
            assert len(predictions) == 2
            assert predictions[0][0] == (9, 10, 11, 12)
            assert mock_predictor.predict_group.called
            
            print("✅ Метод прогнозирования адаптера работает корректно")
            return True

def test_data_utils_integration():
    """Тест интеграции с утилитами данных - ИСПРАВЛЕННАЯ ВЕРСИЯ"""
    print("🔍 ТЕСТ ИНТЕГРАЦИИ С ДАННЫМИ...")
    
    from ml.utils.data_utils import (
        load_dataset,
        save_dataset,
        validate_group,
        compare_groups
    )
    
    with tempfile.TemporaryDirectory() as temp_dir:
        temp_dir_path = Path(temp_dir)
        
        # Тестовые данные
        test_data = ["1 2 3 4", "5 6 7 8", "9 10 11 12"]
        
        # Тест сохранения и загрузки
        test_file = temp_dir_path / 'test_dataset.json'
        
        # ⚡ ИСПРАВЛЕНИЕ: Используем patch для временного файла
        with patch('ml.utils.data_utils.paths.DATASET_FILE', test_file):
            save_dataset(test_data)
            loaded_data = load_dataset()
            
            assert loaded_data == test_data
            print("✅ Сохранение и загрузка dataset работают")
        
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
        return True

def test_basic_functionality():
    """Тест базовой функциональности"""
    print("🔍 ТЕСТ БАЗОВОЙ ФУНКЦИОНАЛЬНОСТИ...")
    
    try:
        # Проверяем импорты
        from web.components.ml_adapter import MLSystemAdapter
        from web.components import sidebar, training_ui, prediction_ui, data_ui, status_ui
        
        # Проверяем ML компоненты
        from ml.core.trainer import EnhancedTrainer
        from ml.core.predictor import EnhancedPredictor
        from ml.learning.self_learning import SelfLearningSystem
        from ml.utils.data_utils import load_dataset, save_dataset
        
        print("✅ Все компоненты импортируются успешно")
        
        # Создаем адаптер
        adapter = MLSystemAdapter()
        
        # Проверяем базовые методы
        status = adapter.get_status()
        assert isinstance(status, dict)
        assert 'is_trained' in status
        assert 'dataset_size' in status
        
        insights = adapter.get_learning_insights()
        assert isinstance(insights, dict)
        
        print("✅ Базовая функциональность работает")
        return True
        
    except Exception as e:
        print(f"❌ Ошибка базовой функциональности: {e}")
        return False

def main():
    """Главная функция тестирования"""
    print("🎯 ИСПРАВЛЕННЫЕ ТЕСТЫ ВЕБ-СЕРВИСА")
    print("=" * 50)
    
    tests = [
        test_ml_adapter_initialization,
        test_ml_adapter_train_method,
        test_ml_adapter_predict_method,
        test_data_utils_integration,
        test_basic_functionality
    ]
    
    passed = 0
    total = len(tests)
    
    for test in tests:
        try:
            if test():
                passed += 1
        except Exception as e:
            print(f"❌ Тест {test.__name__} не пройден: {e}")
    
    print("\n" + "=" * 50)
    print(f"📊 РЕЗУЛЬТАТЫ: {passed}/{total} тестов пройдено")
    
    if passed == total:
        print("🎉 ВСЕ ТЕСТЫ ПРОЙДЕНЫ! Веб-сервис готов к использованию.")
        return 0
    else:
        print("⚠️  НЕКОТОРЫЕ ТЕСТЫ НЕ ПРОЙДЕНЫ. Требуется отладка.")
        return 1

if __name__ == "__main__":
    exit(main())
