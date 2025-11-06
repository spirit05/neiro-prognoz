# final_test.py
#!/usr/bin/env python3
"""
Финальный тест системы
"""

import sys
import os

PROJECT_ROOT = '/home/spirit/Desktop/project'
sys.path.insert(0, PROJECT_ROOT)

def test_all_components():
    """Тестируем все компоненты системы"""
    print("🔍 ФИНАЛЬНОЕ ТЕСТИРОВАНИЕ СИСТЕМЫ")
    print("=" * 50)
    
    tests = [
        ("Конфигурация путей", test_paths),
        ("Система логирования", test_logging),
        ("Веб-интерфейс", test_web_interface),
        ("ML система", test_ml_system),
        ("Сервисы", test_services)
    ]
    
    results = []
    for test_name, test_func in tests:
        try:
            success = test_func()
            results.append((test_name, success))
            status = "✅ ПРОЙДЕН" if success else "❌ ПРОВАЛЕН"
            print(f"{test_name:20} {status}")
        except Exception as e:
            print(f"{test_name:20} ❌ ОШИБКА: {e}")
            results.append((test_name, False))
    
    print("=" * 50)
    
    all_passed = all(success for _, success in results)
    if all_passed:
        print("🎉 ВСЕ ТЕСТЫ ПРОЙДЕНЫ! СИСТЕМА ГОТОВА!")
        return True
    else:
        print("❌ ЕСТЬ ПРОБЛЕМЫ. Требуется дополнительная отладка.")
        return False

def test_paths():
    """Тестируем конфигурацию путей"""
    from config.paths import paths
    assert hasattr(paths, 'DATASET'), "Нет DATASET в paths"
    assert hasattr(paths, 'MODEL'), "Нет MODEL в paths"
    return True

def test_logging():
    """Тестируем систему логирования"""
    from utils.logging_system import setup_all_loggers
    loggers = setup_all_loggers()
    return len(loggers) > 0

def test_web_interface():
    """Тестируем веб-интерфейс"""
    from web.app import main
    return True

def test_ml_system():
    """Тестируем ML систему"""
    from ml.core.system import SimpleNeuralSystem
    system = SimpleNeuralSystem()
    return hasattr(system, 'get_status')

def test_services():
    """Тестируем сервисы"""
    from services.auto_learning.service import AutoLearningService
    service = AutoLearningService()
    return hasattr(service, 'get_service_status')

if __name__ == "__main__":
    success = test_all_components()
    sys.exit(0 if success else 1)