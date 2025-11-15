# [file name]: tests/run_phase3_final.py
"""
Финальный запуск всех тестов этапа 3
"""

import subprocess
import sys
import os

def run_phase3_tests():
    """Запуск тестов этапа 3"""
    tests = [
        "tests/test_feature_engineers_basic.py",
        "tests/test_architecture_integrity.py", 
        "tests/test_orchestrator_integration.py",
        "tests/test_dataprocessor_compatibility.py"  # Новый тест совместимости
    ]
    
    print("🚀 ЗАПУСК ТЕСТОВ ЭТАПА 3: МИГРАЦИЯ FEATURE ENGINEERS")
    print("=" * 60)
    
    results = {}
    
    for test_file in tests:
        print(f"\n📋 Запуск: {test_file}")
        print("-" * 40)
        
        try:
            result = subprocess.run([
                sys.executable, test_file
            ], capture_output=True, text=True, cwd='/opt/model', timeout=30)
            
            if result.returncode == 0:
                print(f"✅ ПРОЙДЕН: {test_file}")
                results[test_file] = "PASSED"
                # Показываем вывод
                if result.stdout:
                    for line in result.stdout.split('\n'):
                        if line.strip() and not line.startswith('='):
                            print(f"   {line}")
            else:
                print(f"❌ ПРОВАЛЕН: {test_file}")
                results[test_file] = "FAILED"
                if result.stderr:
                    print("   Ошибки:")
                    for line in result.stderr.split('\n'):
                        if line.strip():
                            print(f"     {line}")
                            
        except subprocess.TimeoutExpired:
            print(f"⏰ ТАЙМАУТ: {test_file}")
            results[test_file] = "TIMEOUT"
        except Exception as e:
            print(f"💥 ОШИБКА: {test_file} - {e}")
            results[test_file] = "ERROR"
    
    # Итоги
    print(f"\n{'=' * 60}")
    print("🎯 ИТОГИ ЭТАПА 3")
    print(f"{'=' * 60}")
    
    passed = sum(1 for result in results.values() if result == "PASSED")
    total = len(tests)
    
    for test, result in results.items():
        status_icon = "✅" if result == "PASSED" else "❌"
        print(f"{status_icon} {test}: {result}")
    
    print(f"\n📊 Результат: {passed}/{total} тестов пройдено")
    
    if passed == total:
        print("\n🎉 ЭТАП 3 УСПЕШНО ЗАВЕРШЕН!")
        print("✨ Новая модульная система feature engineers готова!")
        print("📋 Выполнено:")
        print("   ✅ Создана структура /ml/features/")
        print("   ✅ Реализован AbstractFeatureEngineer интерфейс")
        print("   ✅ Мигрирован FeatureExtractor → StatisticalEngineer")
        print("   ✅ Мигрирован AdvancedPatternAnalyzer → AdvancedEngineer")
        print("   ✅ Все тесты этапа 3 пройдены")
        return True
    else:
        print("\n⚠️ Требуется доработка перед завершением этапа 3")
        return False

if __name__ == "__main__":
    success = run_phase3_tests()
    sys.exit(0 if success else 1)
