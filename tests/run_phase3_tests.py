# [file name]: tests/run_phase3_tests.py
"""
Запуск всех тестов этапа 3
"""

import subprocess
import sys
import os

def run_tests():
    """Запуск всех тестов этапа 3"""
    tests = [
        "tests/test_feature_equivalence.py",
        "tests/test_dataprocessor_compatibility.py", 
        "tests/test_orchestrator_integration.py"
    ]
    
    results = {}
    
    for test_file in tests:
        print(f"\n{'='*60}")
        print(f"🚀 Запуск теста: {test_file}")
        print(f"{'='*60}")
        
        try:
            # Запускаем тест через subprocess чтобы изолировать импорты
            result = subprocess.run([
                sys.executable, test_file
            ], capture_output=True, text=True, cwd='/opt/model', timeout=30)
            
            if result.returncode == 0:
                print(f"✅ ТЕСТ ПРОЙДЕН: {test_file}")
                results[test_file] = "PASSED"
                # Выводим вывод теста
                if result.stdout:
                    print("📋 Вывод теста:")
                    print(result.stdout)
            else:
                print(f"❌ ТЕСТ ПРОВАЛЕН: {test_file}")
                print(f"Код возврата: {result.returncode}")
                results[test_file] = "FAILED"
                if result.stderr:
                    print("Ошибки:")
                    print(result.stderr)
                    
        except subprocess.TimeoutExpired:
            print(f"⏰ ТЕСТ ЗАВЕРШЕН ПО ТАЙМАУТУ: {test_file}")
            results[test_file] = "TIMEOUT"
        except Exception as e:
            print(f"💥 ОШИБКА ЗАПУСКА ТЕСТА: {test_file} - {e}")
            results[test_file] = "ERROR"
    
    # Сводка результатов
    print(f"\n{'='*60}")
    print("📊 СВОДКА РЕЗУЛЬТАТОВ ЭТАПА 3")
    print(f"{'='*60}")
    
    passed = 0
    for test, result in results.items():
        status_icon = "✅" if result == "PASSED" else "❌"
        print(f"{status_icon} {test}: {result}")
        if result == "PASSED":
            passed += 1
    
    total = len(tests)
    print(f"\n🎯 Результат: {passed}/{total} тестов пройдено")
    
    if passed == total:
        print("🎉 ЭТАП 3 УСПЕШНО ЗАВЕРШЕН! Все тесты пройдены.")
        return True
    else:
        print("⚠️ ЭТАП 3 НЕ ЗАВЕРШЕН. Некоторые тесты не пройдены.")
        return False

if __name__ == "__main__":
    success = run_tests()
    sys.exit(0 if success else 1)
