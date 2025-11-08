# [file name]: tests/test_web_simple.py
"""
Упрощенные тесты веб-сервиса (без pytest)
"""

import sys
import os
import tempfile
import json

sys.path.insert(0, '/opt/dev')

def test_basic_imports():
    """Тест базовых импортов"""
    print("🔍 ТЕСТ БАЗОВЫХ ИМПОРТОВ...")
    
    try:
        from web.components.ml_adapter import MLSystemAdapter
        from web.components.sidebar import show_sidebar
        from web.components.training_ui import show_training_ui
        from web.components.prediction_ui import show_prediction_ui
        from web.components.data_ui import show_data_ui
        from web.components.status_ui import show_status_ui
        
        print("✅ Все веб-компоненты импортируются")
        
        # Проверяем ML компоненты
        from ml.core.trainer import EnhancedTrainer
        from ml.core.predictor import EnhancedPredictor
        from ml.learning.self_learning import SelfLearningSystem
        from ml.utils.data_utils import load_dataset, save_dataset
        
        print("✅ Все ML компоненты импортируются")
        
        return True
        
    except ImportError as e:
        print(f"❌ Ошибка импорта: {e}")
        return False

def test_ml_adapter_simple():
    """Простой тест ML адаптера"""
    print("\n🔍 ПРОСТОЙ ТЕСТ ML АДАПТЕРА...")
    
    try:
        from web.components.ml_adapter import MLSystemAdapter
        
        # Создаем адаптер
        adapter = MLSystemAdapter()
        
        # Проверяем базовые атрибуты
        assert hasattr(adapter, 'is_trained')
        assert hasattr(adapter, 'trainer')
        assert hasattr(adapter, 'predictor')
        
        print("✅ ML адаптер создан успешно")
        
        # Проверяем методы
        status = adapter.get_status()
        assert isinstance(status, dict)
        assert 'is_trained' in status
        assert 'dataset_size' in status
        
        print("✅ Метод get_status() работает")
        
        insights = adapter.get_learning_insights()
        assert isinstance(insights, dict)
        
        print("✅ Метод get_learning_insights() работает")
        
        return True
        
    except Exception as e:
        print(f"❌ Ошибка тестирования адаптера: {e}")
        return False

def test_data_operations():
    """Тест операций с данными"""
    print("\n🔍 ТЕСТ ОПЕРАЦИЙ С ДАННЫМИ...")
    
    try:
        from ml.utils.data_utils import load_dataset, save_dataset, validate_group
        
        with tempfile.TemporaryDirectory() as temp_dir:
            # Тестовые данные
            test_data = ["1 2 3 4", "5 6 7 8", "9 10 11 12"]
            test_file = os.path.join(temp_dir, 'test_data.json')
            
            # Сохраняем данные
            save_dataset(test_data)
            
            # Загружаем данные
            loaded_data = load_dataset()
            assert loaded_data == test_data
            print("✅ Сохранение и загрузка данных работают")
            
            # Тест валидации
            assert validate_group("1 2 3 4") == True
            assert validate_group("1 1 3 4") == False  # Дубликаты
            assert validate_group("1 2 3") == False    # Недостаточно чисел
            print("✅ Валидация групп работает")
            
        return True
        
    except Exception as e:
        print(f"❌ Ошибка операций с данными: {e}")
        return False

def test_web_workflow():
    """Тест базового workflow веб-сервиса"""
    print("\n🔍 ТЕСТ БАЗОВОГО WORKFLOW...")
    
    try:
        from web.components.ml_adapter import MLSystemAdapter
        from ml.utils.data_utils import load_dataset, save_dataset
        
        with tempfile.TemporaryDirectory() as temp_dir:
            # Создаем тестовые данные
            test_data = ["1 2 3 4", "5 6 7 8"] * 30  # 60 групп
            dataset_path = os.path.join(temp_dir, 'dataset.json')
            
            with open(dataset_path, 'w') as f:
                json.dump(test_data, f)
            
            # Создаем адаптер
            adapter = MLSystemAdapter()
            
            # Проверяем статус
            status = adapter.get_status()
            print(f"📊 Статус системы: {status}")
            
            # Проверяем, что система видит данные
            assert status['dataset_size'] == 60
            assert status['has_sufficient_data'] == True
            
            print("✅ Базовый workflow работает")
            
        return True
        
    except Exception as e:
        print(f"❌ Ошибка workflow: {e}")
        return False

def main():
    """Главная функция тестирования"""
    print("🎯 УПРОЩЕННОЕ ТЕСТИРОВАНИЕ ВЕБ-СЕРВИСА")
    print("=" * 50)
    
    tests = [
        test_basic_imports,
        test_ml_adapter_simple, 
        test_data_operations,
        test_web_workflow
    ]
    
    passed = 0
    total = len(tests)
    
    for test in tests:
        if test():
            passed += 1
    
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
