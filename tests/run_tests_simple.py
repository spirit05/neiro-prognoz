# [file name]: tests/run_tests_simple.py (ОБНОВЛЕННЫЙ)
#!/usr/bin/env python3
"""
УПРОЩЕННЫЙ ЗАПУСК ТЕСТОВ с авто-активацией окружения
"""

import os
import sys
import importlib

def activate_virtual_environment():
    """Автоматическая активация виртуального окружения"""
    venv_path = '/opt/project/env'
    
    if not os.path.exists(venv_path):
        print(f"❌ Виртуальное окружение не найдено: {venv_path}")
        return False
    
    # Активируем venv
    activate_script = os.path.join(venv_path, 'bin', 'activate_this.py')
    
    try:
        with open(activate_script) as f:
            exec(f.read(), {'__file__': activate_script})
        print(f"✅ Виртуальное окружение активировано: {venv_path}")
        return True
    except Exception as e:
        print(f"⚠️ Не удалось активировать окружение: {e}")
        return False

def run_simple_tests():
    """Запуск тестов без pytest"""
    print("🎯 ЗАПУСК ТЕСТОВ (упрощенная версия)")
    print("=" * 50)
    
    # Активируем окружение
    if not activate_virtual_environment():
        print("💡 Пытаемся продолжить без активации...")
    
    # Добавляем пути
    PROJECT_PATH = '/opt/project'
    sys.path.insert(0, PROJECT_PATH)
    sys.path.insert(0, os.path.join(PROJECT_PATH, 'tests'))
    
    # Проверяем тестовую среду
    test_files = [
        '/opt/project/tests/test_data/dataset.json',
        '/opt/project/tests/test_data/info.json',
        '/opt/project/tests/test_data/predictions_state.json'
    ]
    
    for file_path in test_files:
        if not os.path.exists(file_path):
            print(f"❌ Тестовый файл {file_path} не найден")
            return False
    
    print("✅ Тестовая среда готова")
    
    # Запускаем простые тесты
    tests_passed = 0
    tests_failed = 0
    
    # Тест 1: Проверка изоляции
    print("\n🧪 Тест 1: Проверка изоляции среды...")
    try:
        from test_safe_operations import test_environment_isolation
        test_environment_isolation()
        print("✅ Тест 1 пройден")
        tests_passed += 1
    except Exception as e:
        print(f"❌ Тест 1 провален: {e}")
        tests_failed += 1
    
    # Тест 2: Проверка содержимого файлов
    print("\n🧪 Тест 2: Проверка содержимого файлов...")
    try:
        from test_safe_operations import test_test_files_content
        test_test_files_content()
        print("✅ Тест 2 пройден")
        tests_passed += 1
    except Exception as e:
        print(f"❌ Тест 2 провален: {e}")
        tests_failed += 1
    
    print("\n" + "=" * 50)
    print(f"📊 РЕЗУЛЬТАТ: {tests_passed} пройдено, {tests_failed} провалено")
    
    if tests_failed == 0:
        print("🎉 ВСЕ ТЕСТЫ ПРОЙДЕНЫ!")
        return True
    else:
        print("💥 ЕСТЬ ПРОВАЛЕННЫЕ ТЕСТЫ!")
        return False

if __name__ == "__main__":
    success = run_simple_tests()
    sys.exit(0 if success else 1)