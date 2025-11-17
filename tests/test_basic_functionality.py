# [file name]: test_basic_functionality.py
"""
Базовые тесты функциональности Data Processing модуля
"""

import sys
import os
sys.path.insert(0, '/opt/model')

def test_data_processor_basic():
    """Тест базовой функциональности DataProcessor"""
    print("🧪 Тест базовой функциональности DataProcessor...")
    
    try:
        from ml.data.processors.data_processor import ModularDataProcessor, DataType
        
        # Создаем процессор
        processor = ModularDataProcessor(history_size=20)
        print("✅ ModularDataProcessor создан")
        
        # Тест извлечения фич
        test_history = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20]
        features = processor.extract_features(test_history)
        
        print(f"✅ Извлечение фич: {len(features)} engineers, фичи: { {k: len(v) for k, v in features.items()} }")
        
        # Тест информации о фичах
        feature_info = processor.get_feature_info()
        print(f"✅ Информация о фичах: {feature_info}")
        
        return True
        
    except Exception as e:
        print(f"❌ Ошибка в базовой функциональности DataProcessor: {e}")
        return False

def test_dataset_manager_basic():
    """Тест базовой функциональности DatasetManager"""
    print("\n🧪 Тест базовой функциональности DatasetManager...")
    
    try:
        from ml.data.providers.dataset_manager import DatasetManager
        
        # Создаем менеджер с временным файлом
        test_path = "/tmp/test_dataset.json"
        manager = DatasetManager(test_path)
        print("✅ DatasetManager создан")
        
        # Тест сохранения и загрузки
        test_data = ["1 2 3 4", "5 6 7 8", "9 10 11 12"]
        success = manager.save_dataset(test_data)
        print(f"✅ Сохранение dataset: {success}")
        
        loaded_data = manager.load_dataset()
        print(f"✅ Загрузка dataset: {len(loaded_data)} групп")
        
        # Тест статистики
        stats = manager.get_dataset_stats()
        print(f"✅ Статистика dataset: {stats}")
        
        # Тест добавления групп
        new_groups = ["13 14 15 16", "17 18 19 20"]
        add_success = manager.add_groups(new_groups)
        print(f"✅ Добавление групп: {add_success}")
        
        # Очистка
        import os
        os.unlink(test_path)
        
        return True
        
    except Exception as e:
        print(f"❌ Ошибка в базовой функциональности DatasetManager: {e}")
        return False

def test_data_validator_basic():
    """Тест базовой функциональности DataValidator"""
    print("\n🧪 Тест базовой функциональности DataValidator...")
    
    try:
        from ml.data.quality.validators import DataValidator
        
        validator = DataValidator()
        print("✅ DataValidator создан")
        
        # Тест валидации групп
        valid_group = "1 2 3 4"
        invalid_group = "1 1 3 4"
        
        is_valid = validator.validate_group(valid_group)
        is_invalid = validator.validate_group(invalid_group)
        
        print(f"✅ Валидация групп: valid={is_valid}, invalid={is_invalid}")
        
        # Тест сравнения групп
        comparison = validator.compare_groups((1, 2, 3, 4), (1, 2, 5, 6))
        print(f"✅ Сравнение групп: {comparison}")
        
        # Тест валидации dataset
        test_groups = ["1 2 3 4", "5 6 7 8", "invalid", "1 1 2 2"]
        validation_stats = validator.validate_dataset(test_groups)
        print(f"✅ Валидация dataset: {validation_stats}")
        
        return True
        
    except Exception as e:
        print(f"❌ Ошибка в базовой функциональности DataValidator: {e}")
        return False

def test_data_processor_advanced():
    """Тест расширенной функциональности DataProcessor"""
    print("\n🧪 Тест расширенной функциональности DataProcessor...")
    
    try:
        from ml.data.processors.data_processor import ModularDataProcessor
        
        processor = ModularDataProcessor(history_size=20)
        
        # Тест подготовки данных обучения
        test_groups = [
            "1 2 3 4", "5 6 7 8", "9 10 11 12", "13 14 15 16",
            "17 18 19 20", "21 22 23 24", "1 3 5 7", "2 4 6 8",
            "10 11 12 13", "14 15 16 17"
        ]
        
        features_batch, targets_batch = processor.prepare_training_data(test_groups)
        
        print(f"✅ Подготовка данных обучения: features={not features_batch.empty}, targets={not targets_batch.empty}")
        if not features_batch.empty:
            print(f"   Features shape: {features_batch.data.shape}")
        if not targets_batch.empty:
            print(f"   Targets shape: {targets_batch.data.shape}")
        
        # Тест создания фич для предсказания
        prediction_batch = processor.create_prediction_features(test_groups[-3:])
        print(f"✅ Создание фич предсказания: {not prediction_batch.empty}")
        if not prediction_batch.empty:
            print(f"   Prediction features shape: {prediction_batch.data.shape}")
        
        return True
        
    except Exception as e:
        print(f"❌ Ошибка в расширенной функциональности DataProcessor: {e}")
        return False

if __name__ == "__main__":
    print("🚀 ЗАПУСК БАЗОВЫХ ТЕСТОВ DATA PROCESSING МОДУЛЯ")
    print("=" * 60)
    
    tests = [
        test_data_processor_basic,
        test_dataset_manager_basic, 
        test_data_validator_basic,
        test_data_processor_advanced
    ]
    
    results = []
    for test in tests:
        try:
            result = test()
            results.append(result)
            print()
        except Exception as e:
            print(f"❌ Тест {test.__name__} упал с ошибкой: {e}")
            results.append(False)
            print()
    
    passed = sum(results)
    total = len(results)
    
    print("=" * 60)
    if passed == total:
        print(f"🎉 ВСЕ БАЗОВЫЕ ТЕСТЫ ПРОЙДЕНЫ! ({passed}/{total})")
        print("✅ Можно переходить к интеграционным тестам")
    else:
        print(f"⚠️  ПРОЙДЕНО БАЗОВЫХ ТЕСТОВ: {passed}/{total}")
        print("❌ Требуется исправление ошибок перед продолжением")
    
    # Сохраняем результат для CI
    exit(0 if passed == total else 1)
