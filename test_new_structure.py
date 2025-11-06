# test_new_structure.py
#!/usr/bin/env python3
"""
Простой тест новой структуры проекта
"""

import sys
import os

# Добавляем корень проекта в путь
PROJECT_ROOT = '/home/spirit/Desktop/project'
sys.path.insert(0, PROJECT_ROOT)

print(f"📍 Корень проекта: {PROJECT_ROOT}")

def test_imports():
    """Тестируем импорты"""
    print("🧪 Тестируем импорты...")
    
    try:
        # Импортируем напрямую из config.paths
        from config.paths import DATASET, MODEL, TELEGRAM_CONFIG
        print("✅ Пути импортируются")
        print(f"📁 DATASET: {DATASET}")
        print(f"📁 MODEL: {MODEL}")
        print(f"📁 TELEGRAM_CONFIG: {TELEGRAM_CONFIG}")
        
        # Тестируем константы
        from config.constants import MAX_API_RETRIES, SCHEDULE_MINUTES
        print(f"⚙️  MAX_API_RETRIES: {MAX_API_RETRIES}")
        print(f"⚙️  SCHEDULE_MINUTES: {SCHEDULE_MINUTES}")
        
        # Тестируем логирование
        from config.logging_config import setup_logging
        logger = setup_logging('test_structure')
        logger.info("✅ Логирование работает")
        
        print("🎉 Все импорты работают!")
        return True
        
    except Exception as e:
        print(f"❌ Ошибка импорта: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_paths_exist():
    """Проверяем что пути существуют"""
    print("\n📁 Проверяем существование путей...")
    
    from config.paths import DATASETS_DIR, MODELS_DIR, ANALYTICS_DIR, LOGS_DIR, TELEGRAM_CONFIG
    
    required_dirs = [DATASETS_DIR, MODELS_DIR, ANALYTICS_DIR, LOGS_DIR]
    
    for directory in required_dirs:
        if os.path.exists(directory):
            print(f"✅ {directory} существует")
        else:
            print(f"❌ {directory} не существует")
    
    if os.path.exists(TELEGRAM_CONFIG):
        print(f"✅ {TELEGRAM_CONFIG} существует")
    else:
        print(f"⚠️  {TELEGRAM_CONFIG} не существует (но это нормально)")

def test_file_operations():
    """Проверяем базовые файловые операции"""
    print("\n📝 Тестируем файловые операции...")
    
    from config.paths import DATASETS_DIR, DATASET
    
    # Пробуем создать тестовый файл
    test_file = os.path.join(DATASETS_DIR, 'test.txt')
    try:
        with open(test_file, 'w') as f:
            f.write("test")
        print("✅ Запись файла работает")
        
        with open(test_file, 'r') as f:
            content = f.read()
        print("✅ Чтение файла работает")
        
        os.remove(test_file)
        print("✅ Удаление файла работает")
        
    except Exception as e:
        print(f"❌ Ошибка файловых операций: {e}")

if __name__ == "__main__":
    print(f"🚀 Запуск теста новой структуры")
    print("=" * 50)
    
    success = test_imports()
    test_paths_exist()
    test_file_operations()
    
    print("\n" + "=" * 50)
    if success:
        print("🎉 ФАЗА 1 ЗАВЕРШЕНА УСПЕШНО!")
        print("📋 Можно переходить к Фазе 2")
    else:
        print("💥 Есть проблемы с новой структурой!")
        sys.exit(1)