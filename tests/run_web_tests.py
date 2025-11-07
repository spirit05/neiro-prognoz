# [file name]: tests/run_web_tests.py
"""
Главный скрипт для запуска всех тестов веб-сервиса
"""

import sys
import os
import subprocess
import argparse

# Добавляем пути
sys.path.insert(0, '/opt/dev')

def run_integration_tests():
    """Запуск интеграционных тестов"""
    print("=" * 60)
    print("🚀 ЗАПУСК ИНТЕГРАЦИОННЫХ ТЕСТОВ")
    print("=" * 60)
    
    try:
        # Импортируем и запускаем тесты напрямую
        from tests.test_web_integration import (
            test_ml_adapter_initialization,
            test_ml_adapter_train_method,
            test_ml_adapter_predict_method,
            test_ml_adapter_add_data_method,
            test_web_components_import,
            test_utils_functions,
            test_data_utils_integration,
            test_ml_system_integration,
            test_config_integration
        )
        
        # Запускаем все тесты
        test_functions = [
            test_ml_adapter_initialization,
            test_ml_adapter_train_method,
            test_ml_adapter_predict_method,
            test_ml_adapter_add_data_method,
            test_web_components_import,
            test_utils_functions,
            test_data_utils_integration,
            test_ml_system_integration,
            test_config_integration
        ]
        
        for test_func in test_functions:
            try:
                test_func()
            except Exception as e:
                print(f"❌ Тест {test_func.__name__} не пройден: {e}")
                return False
        
        print("✅ ВСЕ ИНТЕГРАЦИОННЫЕ ТЕСТЫ ПРОЙДЕНЫ!")
        return True
        
    except Exception as e:
        print(f"❌ Ошибка запуска интеграционных тестов: {e}")
        return False

def run_functional_tests():
    """Запуск функциональных тестов"""
    print("\n" + "=" * 60)
    print("🚀 ЗАПУСК ФУНКЦИОНАЛЬНЫХ ТЕСТОВ")
    print("=" * 60)
    
    try:
        from tests.test_web_functional import (
            test_complete_workflow,
            test_error_handling,
            test_ui_components
        )
        
        test_functions = [
            test_complete_workflow,
            test_error_handling,
            test_ui_components
        ]
        
        for test_func in test_functions:
            try:
                test_func()
            except Exception as e:
                print(f"❌ Тест {test_func.__name__} не пройден: {e}")
                return False
        
        print("✅ ВСЕ ФУНКЦИОНАЛЬНЫЕ ТЕСТЫ ПРОЙДЕНЫ!")
        return True
        
    except Exception as e:
        print(f"❌ Ошибка запуска функциональных тестов: {e}")
        return False

def run_pytest_tests():
    """Запуск тестов через pytest"""
    print("\n" + "=" * 60)
    print("🚀 ЗАПУСК ТЕСТОВ ЧЕРЕЗ PYTEST")
    print("=" * 60)
    
    try:
        # Запускаем pytest для тестовых файлов
        result = subprocess.run([
            'python', '-m', 'pytest', 
            'tests/test_web_integration.py', 
            'tests/test_web_functional.py',
            '-v'
        ], cwd='/opt/dev', capture_output=True, text=True)
        
        print(result.stdout)
        if result.stderr:
            print("STDERR:", result.stderr)
        
        return result.returncode == 0
        
    except Exception as e:
        print(f"❌ Ошибка запуска pytest: {e}")
        return False

def main():
    """Главная функция запуска тестов"""
    parser = argparse.ArgumentParser(description='Запуск тестов веб-сервиса')
    parser.add_argument('--type', choices=['all', 'integration', 'functional', 'pytest'], 
                       default='all', help='Тип тестов для запуска')
    
    args = parser.parse_args()
    
    print("🎯 ТЕСТИРОВАНИЕ ВЕБ-СЕРВИСА С МОДУЛЬНОЙ АРХИТЕКТУРОЙ")
    print("📅 Начало тестирования...\n")
    
    success = True
    
    if args.type in ['all', 'integration']:
        if not run_integration_tests():
            success = False
    
    if args.type in ['all', 'functional']:
        if not run_functional_tests():
            success = False
    
    if args.type in ['all', 'pytest']:
        if not run_pytest_tests():
            success = False
    
    print("\n" + "=" * 60)
    if success:
        print("🎉 ВСЕ ТЕСТЫ ПРОЙДЕНЫ УСПЕШНО!")
        print("✅ Веб-сервис готов к использованию в новой модульной архитектуре!")
    else:
        print("❌ НЕКОТОРЫЕ ТЕСТЫ НЕ ПРОЙДЕНЫ!")
        print("⚠️  Требуется отладка перед использованием")
    
    print("=" * 60)
    return 0 if success else 1

if __name__ == "__main__":
    exit(main())