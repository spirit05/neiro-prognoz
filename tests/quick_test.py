# [file name]: tests/quick_test.py
"""
Быстрый тест работоспособности
"""

import sys
sys.path.insert(0, '/opt/dev')

def quick_test():
    """Быстрый тест основных компонентов"""
    print("🚀 БЫСТРЫЙ ТЕСТ РАБОТОСПОСОБНОСТИ")
    print("=" * 40)
    
    try:
        # 1. Проверяем импорты
        from web.components.ml_adapter import MLSystemAdapter
        print("✅ ML адаптер импортирован")
        
        # 2. Создаем адаптер
        adapter = MLSystemAdapter()
        print("✅ ML адаптер создан")
        
        # 3. Проверяем статус
        status = adapter.get_status()
        print(f"✅ Статус системы: обучена={status['is_trained']}, данные={status['dataset_size']}")
        
        # 4. Проверяем данные
        from ml.utils.data_utils import load_dataset
        data = load_dataset()
        print(f"✅ Данные загружены: {len(data)} групп")
        
        # 5. Проверяем валидацию
        from ml.utils.data_utils import validate_group
        assert validate_group("1 2 3 4") == True
        assert validate_group("invalid") == False
        print("✅ Валидация работает")
        
        print("\n🎉 ВСЕ ОСНОВНЫЕ КОМПОНЕНТЫ РАБОТАЮТ!")
        return True
        
    except Exception as e:
        print(f"❌ Ошибка: {e}")
        return False

if __name__ == "__main__":
    success = quick_test()
    exit(0 if success else 1)
