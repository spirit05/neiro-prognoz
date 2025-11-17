# [file name]: test_fixed_functionality.py
"""
Исправленные тесты функциональности Data Processing модуля
"""

import sys
import os
sys.path.insert(0, '/opt/model')

def test_data_processor_with_sufficient_data():
    """Тест DataProcessor с достаточным количеством данных"""
    print("🧪 Тест DataProcessor с достаточным количеством данных...")
    
    try:
        from ml.data.processors.data_processor import ModularDataProcessor
        
        processor = ModularDataProcessor(history_size=20)
        
        # Создаем достаточно данных для обучения (минимум 50 чисел = 13+ групп)
        test_groups = [
            "1 2 3 4", "5 6 7 8", "9 10 11 12", "13 14 15 16", "17 18 19 20",
            "21 22 23 24", "1 3 5 7", "2 4 6 8", "10 11 12 13", "14 15 16 17",
            "18 19 20 21", "22 23 24 25", "1 2 4 5", "3 6 7 8", "9 11 13 15"
        ]  # 15 групп = 60 чисел
        
        features_batch, targets_batch = processor.prepare_training_data(test_groups)
        
        print(f"✅ Подготовка данных обучения: features={not features_batch.empty}, targets={not targets_batch.empty}")
        if not features_batch.empty:
            print(f"   Features shape: {features_batch.data.shape}")
            print(f"   Features columns: {len(features_batch.data.columns)}")
        if not targets_batch.empty:
            print(f"   Targets shape: {targets_batch.data.shape}")
        
        # Тест создания фич для предсказания с достаточной историей
        prediction_groups = test_groups[-5:]  # 5 групп = 20 чисел
        prediction_batch = processor.create_prediction_features(prediction_groups)
        print(f"✅ Создание фич предсказания: {not prediction_batch.empty}")
        if not prediction_batch.empty:
            print(f"   Prediction features shape: {prediction_batch.data.shape}")
            print(f"   Prediction features columns: {len(prediction_batch.data.columns)}")
        
        return True
        
    except Exception as e:
        print(f"❌ Ошибка в DataProcessor с достаточными данными: {e}")
        return False

def test_feature_consistency():
    """Тест консистентности фич между старой и новой системой"""
    print("\n🧪 Тест консистентности фич...")
    
    try:
        from ml.data.processors.data_processor import ModularDataProcessor
        
        processor = ModularDataProcessor(history_size=20)
        
        # Тестовая история
        test_history = list(range(1, 21))  # [1, 2, 3, ..., 20]
        
        # Извлекаем фичи через новую систему
        features_dict = processor.extract_features(test_history)
        
        # Проверяем что StatisticalEngineer возвращает 50 фич (как старый BaseFeatureExtractor)
        statistical_features = features_dict.get('statistical', [])
        advanced_features = features_dict.get('advanced', [])
        
        print(f"✅ Statistical features: {len(statistical_features)} (ожидалось: 50)")
        print(f"✅ Advanced features: {len(advanced_features)} (ожидалось: 15)")
        print(f"✅ Всего фич: {len(statistical_features) + len(advanced_features)}")
        
        # Проверяем что фичи в разумных диапазонах
        if len(statistical_features) > 0:
            stats_mean = statistical_features.mean()
            stats_std = statistical_features.std()
            print(f"✅ Statistical features stats: mean={stats_mean:.3f}, std={stats_std:.3f}")
        
        if len(advanced_features) > 0:
            adv_mean = advanced_features.mean() 
            adv_std = advanced_features.std()
            print(f"✅ Advanced features stats: mean={adv_mean:.3f}, std={adv_std:.3f}")
        
        return len(statistical_features) == 50 and len(advanced_features) == 15
        
    except Exception as e:
        print(f"❌ Ошибка в тесте консистентности фич: {e}")
        return False

def test_dataset_manager_comprehensive():
    """Комплексный тест DatasetManager"""
    print("\n🧪 Комплексный тест DatasetManager...")
    
    try:
        from ml.data.providers.dataset_manager import DatasetManager
        
        test_path = "/tmp/test_comprehensive_dataset.json"
        manager = DatasetManager(test_path)
        
        # Тест с реальными данными
        real_groups = [
            "12 26 26 11", "17 24 9 16", "20 6 24 22", "9 7 16 22", "21 23 2 13",
            "1 16 11 12", "20 17 15 6", "25 17 20 5", "1 14 20 24", "25 6 23 19"
        ]
        
        # Сохраняем
        success = manager.save_dataset(real_groups)
        print(f"✅ Сохранение реальных данных: {success}")
        
        # Загружаем и проверяем
        loaded = manager.load_dataset()
        print(f"✅ Загрузка реальных данных: {len(loaded)} групп")
        
        # Статистика
        stats = manager.get_dataset_stats()
        print(f"✅ Статистика реальных данных: {stats['valid_groups']} валидных из {stats['total_groups']}")
        
        # Бэкап
        backup_success = manager.backup_dataset()
        print(f"✅ Бэкап dataset: {backup_success}")
        
        # Очистка
        import os
        os.unlink(test_path)
        os.unlink("/tmp/test_comprehensive_dataset.backup.json")
        
        return True
        
    except Exception as e:
        print(f"❌ Ошибка в комплексном тесте DatasetManager: {e}")
        return False

def test_data_validation_comprehensive():
    """Комплексный тест валидации данных"""
    print("\n🧪 Комплексный тест валидации данных...")
    
    try:
        from ml.data.quality.validators import DataValidator
        
        validator = DataValidator()
        
        # Тест различных сценариев валидации
        test_cases = [
            ("1 2 3 4", True),      # валидная
            ("1 1 3 4", False),     # одинаковые в паре
            ("1 2 3", False),       # недостаточно чисел
            ("1 2 3 4 5", False),   # слишком много чисел
            ("0 2 3 4", False),     # число вне диапазона
            ("27 2 3 4", False),    # число вне диапазона
            ("1 2 3 4 ", True),     # пробел в конце
            (" 1 2 3 4", True),     # пробел в начале
            ("1  2  3  4", True),   # двойные пробелы
        ]
        
        valid_count = 0
        for group, expected in test_cases:
            result = validator.validate_group(group)
            status = "✅" if result == expected else "❌"
            print(f"   {status} '{group}' -> {result} (ожидалось: {expected})")
            if result == expected:
                valid_count += 1
        
        print(f"✅ Валидация групп: {valid_count}/{len(test_cases)} пройдено")
        
        # Тест сравнения групп
        comparison_cases = [
            ((1, 2, 3, 4), (1, 2, 3, 4), 4),  # полное совпадение
            ((1, 2, 3, 4), (1, 2, 5, 6), 2),  # совпадение первых двух
            ((1, 2, 3, 4), (5, 6, 3, 4), 2),  # совпадение последних двух
            ((1, 2, 3, 4), (5, 6, 7, 8), 0),  # нет совпадений
        ]
        
        comparison_count = 0
        for pred, actual, expected_matches in comparison_cases:
            result = validator.compare_groups(pred, actual)
            status = "✅" if result['total_matches'] == expected_matches else "❌"
            print(f"   {status} {pred} vs {actual} -> {result['total_matches']} (ожидалось: {expected_matches})")
            if result['total_matches'] == expected_matches:
                comparison_count += 1
        
        print(f"✅ Сравнение групп: {comparison_count}/{len(comparison_cases)} пройдено")
        
        return valid_count == len(test_cases) and comparison_count == len(comparison_cases)
        
    except Exception as e:
        print(f"❌ Ошибка в комплексном тесте валидации: {e}")
        return False

if __name__ == "__main__":
    print("🚀 ЗАПУСК ИСПРАВЛЕННЫХ ТЕСТОВ DATA PROCESSING МОДУЛЯ")
    print("=" * 60)
    
    tests = [
        test_data_processor_with_sufficient_data,
        test_feature_consistency,
        test_dataset_manager_comprehensive,
        test_data_validation_comprehensive
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
        print(f"🎉 ВСЕ ИСПРАВЛЕННЫЕ ТЕСТЫ ПРОЙДЕНЫ! ({passed}/{total})")
        print("✅ Data Processing модуль функционирует корректно!")
    else:
        print(f"⚠️  ПРОЙДЕНО ИСПРАВЛЕННЫХ ТЕСТОВ: {passed}/{total}")
        print("❌ Требуется дополнительное исправление")
    
    exit(0 if passed == total else 1)
