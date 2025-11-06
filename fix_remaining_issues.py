# fix_remaining_issues.py
#!/usr/bin/env python3
"""
Исправление оставшихся проблем после автоматического исправления
"""

import os
import sys

PROJECT_ROOT = '/home/spirit/Desktop/project'
sys.path.insert(0, PROJECT_ROOT)

def check_and_fix_paths_py():
    """Проверяем и исправляем config/paths.py"""
    print("🔧 Проверяем config/paths.py...")
    
    paths_file = os.path.join(PROJECT_ROOT, 'config', 'paths.py')
    
    with open(paths_file, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Проверяем наличие класса Paths
    if 'class Paths:' not in content:
        print("❌ Класс Paths отсутствует в config/paths.py")
        return False
    
    # Проверяем создание экземпляра
    if 'paths = Paths()' not in content:
        print("❌ Создание экземпляра paths отсутствует")
        return False
    
    print("✅ config/paths.py в порядке")
    return True

def check_utils_module():
    """Проверяем наличие модуля utils"""
    print("🔧 Проверяем модуль utils...")
    
    utils_dir = os.path.join(PROJECT_ROOT, 'utils')
    logging_system_file = os.path.join(utils_dir, 'logging_system.py')
    
    if not os.path.exists(utils_dir):
        print("❌ Директория utils не существует")
        os.makedirs(utils_dir)
        print("✅ Создана директория utils")
    
    if not os.path.exists(logging_system_file):
        print("❌ Файл utils/logging_system.py не существует")
        return False
    
    print("✅ Модуль utils существует")
    return True

def test_imports():
    """Тестируем основные импорты"""
    print("🔧 Тестируем импорты...")
    
    try:
        from config.paths import paths
        print("✅ config.paths импортируется")
        
        from utils.logging_system import get_training_logger
        print("✅ utils.logging_system импортируется")
        
        from web.app import main
        print("✅ web.app импортируется")
        
        return True
    except Exception as e:
        print(f"❌ Ошибка импорта: {e}")
        return False

def main():
    """Основная функция"""
    print("🚀 Исправление оставшихся проблем...")
    
    success1 = check_and_fix_paths_py()
    success2 = check_utils_module()
    success3 = test_imports()
    
    print("\n" + "=" * 50)
    if success1 and success2 and success3:
        print("🎉 Все проблемы исправлены!")
        print("📋 Система готова к запуску!")
    else:
        print("💥 Есть нерешенные проблемы!")
        
        if not success1:
            print("   • Нужно восстановить config/paths.py")
        if not success2:
            print("   • Нужно создать utils/logging_system.py")
        if not success3:
            print("   • Есть ошибки импорта")

if __name__ == "__main__":
    main()