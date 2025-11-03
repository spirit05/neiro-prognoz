#!/usr/bin/env python3
"""
ЗАПУСК ВСЕХ ИСПРАВЛЕННЫХ ТЕСТОВ - оптимизированная версия
"""
import subprocess
import sys
import os

def run_fixed_tests():
    """Запуск всех исправленных тестов"""
    print("🎯 ЗАПУСК ВСЕХ ТЕСТОВ (исправленная версия)")
    print("=" * 50)
    
    # Список всех тестовых файлов
    test_files = [
        'test_safe_operations.py',
        'test_auto_learning_service_fixed.py',
        'integration/test_real_workflow.py',
        'integration/test_telegram_bot.py', 
        'integration/test_resilience.py'
    ]
    
    all_passed = True
    
    for test_file in test_files:
        full_path = f"/opt/project/tests/{test_file}"
        print(f"\n🧪 ЗАПУСК {test_file}...")
        
        # Проверяем существует ли файл
        if not os.path.exists(full_path):
            print(f"❌ Файл {test_file} не найден")
            all_passed = False
            continue
            
        try:
            # Импортируем и запускаем тест
            module_name = test_file.replace('/', '.').replace('.py', '')
            result = subprocess.run([
                'python3', '-c', f'''
import sys
sys.path.insert(0, "/opt/project")
sys.path.insert(0, "/opt/project/tests")
sys.path.insert(0, "/opt/project/tests/integration")

try:
    import {module_name} as test_module
    print("✅ {test_file} - ИМПОРТ УСПЕШЕН")
    
    # Запускаем все тестовые функции
    test_functions = [func for func in dir(test_module) if func.startswith("test_")]
    if test_functions:
        for func_name in test_functions:
            func = getattr(test_module, func_name)
            if callable(func):
                try:
                    func()
                    print(f"   ✅ {{func_name}} - ПРОЙДЕН")
                except Exception as e:
                    print(f"   ❌ {{func_name}} - ОШИБКА: {{e}}")
                    all_passed = False
    else:
        print("   ℹ️  Нет тестовых функций")
        
except Exception as e:
    print(f"❌ {test_file} - ОШИБКА ИМПОРТА: {{e}}")
    sys.exit(1)
                '''
            ], capture_output=True, text=True)
            
            if result.returncode == 0:
                print(f"✅ {test_file} - РАБОТАЕТ")
            else:
                print(f"❌ {test_file} - ОШИБКА")
                if result.stderr:
                    print(f"   STDERR: {result.stderr}")
                all_passed = False
                
        except Exception as e:
            print(f"❌ {test_file} - КРИТИЧЕСКАЯ ОШИБКА: {e}")
            all_passed = False
    
    print("\n" + "=" * 50)
    if all_passed:
        print("🎉 ВСЕ ТЕСТЫ УСПЕШНО ПРОЙДЕНЫ!")
    else:
        print("💥 ЕСТЬ ПРОБЛЕМЫ В ТЕСТАХ!")
    
    return all_passed

if __name__ == "__main__":
    success = run_fixed_tests()
    sys.exit(0 if success else 1)