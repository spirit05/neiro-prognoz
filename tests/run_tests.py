# [file name]: tests/run_tests.py (ИСПРАВЛЕННЫЕ ПУТИ)
#!/usr/bin/env python3
"""
ЗАПУСК ВСЕХ ТЕСТОВ с исправленными путями
"""

import os
import sys
import subprocess

def setup_test_environment_if_needed():
    """Автоматическая настройка тестовой среды если нужно"""
    test_dirs = [
        '/opt/project/tests/test_data', 
        '/opt/project/tests/test_config',
        '/opt/project/tests/test_logs'
    ]
    
    # Проверяем нужные файлы
    required_files = [
        '/opt/project/tests/test_data/dataset.json',
        '/opt/project/tests/test_data/info.json',
        '/opt/project/tests/test_data/predictions_state.json'
    ]
    
    environment_ready = all(os.path.exists(dir_path) for dir_path in test_dirs) and \
                       all(os.path.exists(file_path) for file_path in required_files)
    
    if not environment_ready:
        print("🔧 Тестовая среда не готова, запускаю настройку...")
        setup_result = subprocess.run([
            'python3', 'setup_test_environment.py'
        ], cwd='/opt/project/tests', capture_output=True, text=True)
        
        if setup_result.returncode == 0:
            print("✅ Тестовая среда настроена автоматически")
            return True
        else:
            print(f"❌ Ошибка настройки тестовой среды: {setup_result.stderr}")
            return False
    
    return True

def run_tests():
    """Запуск всех тестов"""
    print("🎯 ЗАПУСК ТЕСТОВ В ИЗОЛИРОВАННОЙ СРЕДЕ")
    print("=" * 50)
    
    # Автоматически настраиваем среду если нужно
    if not setup_test_environment_if_needed():
        return False
    
    # Используем Python из виртуального окружения
    venv_python = '/opt/project/env/bin/python3'
    
    if not os.path.exists(venv_python):
        print(f"❌ Python из venv не найден: {venv_python}")
        print("💡 Используем системный Python (может не работать)")
        venv_python = 'python3'
    
    # Проверяем pytest в выбранном Python
    check_result = subprocess.run([venv_python, '-c', 'import pytest'], capture_output=True)
    if check_result.returncode != 0:
        print(f"❌ pytest не установлен в {venv_python}")
        print("💡 Устанавливаю pytest автоматически...")
        install_result = subprocess.run([
            '/opt/project/env/bin/pip', 'install', 'pytest'
        ], capture_output=True, text=True)
        
        if install_result.returncode != 0:
            print(f"❌ Ошибка установки pytest: {install_result.stderr}")
            return False
        else:
            print("✅ pytest установлен автоматически")
    
    print(f"✅ Используем: {venv_python}")
    print("✅ Тестовая среда готова")
    
    # Запускаем тесты - используем правильные пути
    test_files = [
        'test_safe_operations.py',
        'test_auto_learning_service.py'
    ]
    
    all_passed = True
    
    for test_file in test_files:
        test_file_path = os.path.join('/opt/project/tests', test_file)
        print(f"\n🧪 ЗАПУСК {test_file}...")
        
        result = subprocess.run([
            venv_python, '-m', 'pytest', 
            test_file_path, 
            '-v', 
            '--tb=short'
        ], capture_output=True, text=True)
        
        if result.returncode == 0:
            print(f"✅ {test_file} - ТЕСТЫ ПРОЙДЕНЫ")
            # Показываем успешные тесты
            for line in result.stdout.split('\n'):
                if 'PASSED' in line and 'test_' in line:
                    print(f"   {line.strip()}")
        else:
            print(f"❌ {test_file} - ТЕСТЫ ПРОВАЛЕНЫ")
            print("\n" + "="*40)
            print("ДЕТАЛИ ОШИБКИ:")
            print(result.stdout)
            if result.stderr:
                print("STDERR:", result.stderr)
            print("="*40 + "\n")
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