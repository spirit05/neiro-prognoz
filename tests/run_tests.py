# [file name]: tests/run_tests.py (ОБНОВЛЕННЫЙ)
#!/usr/bin/env pyt////hon3
"""
ЗАПУСК ВСЕХ ТЕСТОВ с автоматической активацией окружения
"""

import os
import sys
import subprocess

def activate_virtual_environment():
    """Автоматическая активация виртуального окружения"""
    venv_path = '/opt/project/env'
    
    if not os.path.exists(venv_path):
        print(f"❌ Виртуальное окружение не найдено: {venv_path}")
        print("💡 Проверьте путь или установите зависимости вручную")
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
        print("💡 Пытаемся продолжить без активации...")
        return True

def run_tests():
    """Запуск всех тестов"""
    print("🎯 ЗАПУСК ТЕСТОВ В ИЗОЛИРОВАННОЙ СРЕДЕ")
    print("=" * 50)
    
    # Активируем окружение
    if not activate_virtual_environment():
        return False
    
    # Добавляем пути
    PROJECT_PATH = '/opt/project'
    sys.path.insert(0, PROJECT_PATH)
    sys.path.insert(0, os.path.join(PROJECT_PATH, 'tests'))
    
    # Проверяем существование тестовой среды
    test_dirs = [
        '/opt/project/tests',
        '/opt/project/tests/test_data', 
        '/opt/project/tests/test_config',
        '/opt/project/tests/test_logs'
    ]
    
    for dir_path in test_dirs:
        if not os.path.exists(dir_path):
            print(f"❌ Тестовая директория {dir_path} не найдена")
            print("💡 Сначала запустите: python3 tests/setup_test_environment.py")
            return False
    
    print("✅ Тестовая среда готова")
    
    # Запускаем тесты
    test_files = [
        'tests/test_safe_operations.py',
        'tests/test_auto_learning_service.py'
    ]
    
    all_passed = True
    
    for test_file in test_files:
        print(f"\n🧪 ЗАПУСК {test_file}...")
        result = subprocess.run([
            'python3', '-m', 'pytest', 
            test_file, 
            '-v', 
            '--tb=short'
        ], cwd=PROJECT_PATH, capture_output=True, text=True)
        
        if result.returncode == 0:
            print(f"✅ {test_file} - ТЕСТЫ ПРОЙДЕНЫ")
        else:
            print(f"❌ {test_file} - ТЕСТЫ ПРОВАЛЕНЫ")
            print(result.stdout)
            print(result.stderr)
            all_passed = False
    
    print("\n" + "=" * 50)
    if all_passed:
        print("🎉 ВСЕ ТЕСТЫ УСПЕШНО ПРОЙДЕНЫ!")
        print("💚 Тестовая среда полностью изолирована от продакшена")
    else:
        print("💥 НЕКОТОРЫЕ ТЕСТЫ ПРОВАЛЕНЫ!")
        
    return all_passed

if __name__ == "__main__":
    success = run_tests()
    sys.exit(0 if success else 1)