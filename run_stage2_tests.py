#!/usr/bin/env python3
"""
ЗАПУСК ИСПРАВЛЕННЫХ ТЕСТОВ ЭТАПА 2
"""
import subprocess
import sys
import os
from pathlib import Path

def run_fixed_tests():
    """Запуск исправленных тестов ЭТАПА 2"""
    print("🚀 ЗАПУСК ИСПРАВЛЕННЫХ ТЕСТОВ ЭТАПА 2")
    print("=" * 60)
    
    # Добавление путей для импортов
    project_root = Path(__file__).parent
    sys.path.insert(0, str(project_root))
    
    test_files = [
        "test_stage2_minimal.py",
        "test_stage2_abstract_interface.py"
    ]
    
    all_passed = True
    
    for test_file in test_files:
        if not Path(test_file).exists():
            print(f"❌ Файл тестов не найден: {test_file}")
            continue
            
        print(f"\n📋 Запуск тестов: {test_file}")
        print("-" * 40)
        
        result = subprocess.run([
            sys.executable, "-m", "pytest", test_file, 
            "-v", "--tb=short"
        ], capture_output=True, text=True)
        
        if result.returncode == 0:
            print("✅ ТЕСТЫ ПРОЙДЕНЫ")
            print(result.stdout)
        else:
            print("❌ ТЕСТЫ НЕ ПРОЙДЕНЫ")
            print(result.stdout)
            if result.stderr:
                print("Ошибки:")
                print(result.stderr)
            all_passed = False
    
    print("\n" + "=" * 60)
    if all_passed:
        print("🎉 ОСНОВНЫЕ ТЕСТЫ ЭТАПА 2 УСПЕШНО ПРОЙДЕНЫ!")
    else:
        print("💥 НЕКОТОРЫЕ ТЕСТЫ НЕ ПРОЙДЕНЫ")
        
    return all_passed

if __name__ == "__main__":
    success = run_fixed_tests()
    sys.exit(0 if success else 1)
