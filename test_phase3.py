# test_phase3_fixed.py
#!/usr/bin/env python3
"""
Тест Фазы 3 - ИСПРАВЛЕННАЯ ВЕРСИЯ
"""

import sys
import os

PROJECT_ROOT = '/home/spirit/Desktop/project'
sys.path.insert(0, PROJECT_ROOT)

def test_imports():
    """Тестируем импорты новых модулей"""
    print("🧪 Тестируем импорты ML системы...")

    try:
        # Тестируем главную систему
        from ml.core.system import SimpleNeuralSystem
        system = SimpleNeuralSystem()
        print("✅ SimpleNeuralSystem импортируется")

        # Тестируем загрузчик данных
        from ml.data.data_loader import load_dataset, save_dataset, validate_group
        print("✅ DataLoader импортируется")

        # Тестируем основные ML компоненты
        from ml.core.trainer import EnhancedTrainer
        from ml.core.predictor import EnhancedPredictor
        from ml.core.model import EnhancedNumberPredictor
        print("✅ ML компоненты импортируются")

        print("🎉 Все ML модули импортируются корректно!")
        return True

    except Exception as e:
        print(f"❌ Ошибка импорта ML системы: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_ml_system_creation():
    """Тестируем создание ML системы"""
    print("\n🔧 Тестируем создание ML системы...")

    try:
        from ml.core.system import SimpleNeuralSystem

        system = SimpleNeuralSystem()

        # Проверяем основные атрибуты
        assert hasattr(system, 'is_trained'), "Система должна иметь атрибут is_trained"
        assert hasattr(system, 'train'), "Система должна иметь метод train"
        assert hasattr(system, 'predict'), "Система должна иметь метод predict"
        assert hasattr(system, 'add_data_and_retrain'), "Система должна иметь метод add_data_and_retrain"

        # Проверяем статус
        status = system.get_status()
        assert 'is_trained' in status, "Статус должен содержать is_trained"
        assert 'dataset_size' in status, "Статус должен содержать dataset_size"

        print("✅ ML система создается корректно (несмотря на предупреждения)")
        return True

    except Exception as e:
        print(f"❌ Ошибка создания ML системы: {e}")
        return False

def test_data_operations():
    """Тестируем операции с данными"""
    print("\n📊 Тестируем операции с данными...")

    try:
        from ml.data.data_loader import validate_group, save_dataset, load_dataset

        # Тестируем валидацию
        assert validate_group("1 2 3 4") == True, "Валидная группа должна проходить"
        assert validate_group("1 1 3 4") == False, "Дубли в парах должны быть невалидны"
        assert validate_group("1 2 3") == False, "Неполная группа должна быть невалидна"

        print("✅ Операции с данными работают")
        return True

    except Exception as e:
        print(f"❌ Ошибка операций с данными: {e}")
        return False

def test_service_ml_integration():
    """Тестируем интеграцию сервиса с ML"""
    print("\n🔗 Тестируем интеграцию сервиса с ML...")

    try:
        from services.auto_learning.service import AutoLearningService

        service = AutoLearningService()

        # Проверяем что ML система инициализирована
        assert service.system is not None, "Сервис должен иметь инициализированную ML систему"

        # Проверяем статус через сервис
        status = service.get_service_status()
        assert 'model_trained' in status, "Статус сервиса должен содержать model_trained"
        assert 'system_initialized' in status, "Статус сервиса должен содержать system_initialized"
        assert 'max_consecutive_errors' in status, "Статус сервиса должен содержать max_consecutive_errors"  # ← Ключевая проверка

        print("✅ Интеграция сервиса с ML работает")
        return True

    except Exception as e:
        print(f"❌ Ошибка интеграции сервиса с ML: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_missing_modules():
    """Тестируем создание отсутствующих модулей"""
    print("\n🔨 Тестируем создание отсутствующих модулей...")

    try:
        # Создаем ансамблевый предсказатель
        from ml.ensemble.ensemble import EnsemblePredictor
        ensemble = EnsemblePredictor()
        print("✅ EnsemblePredictor создан")

        # Создаем систему самообучения
        from ml.learning.self_learning import SelfLearningSystem
        self_learning = SelfLearningSystem()
        print("✅ SelfLearningSystem создан")

        # Создаем Telegram нотификатор
        from services.telegram.notifier import TelegramNotifier
        notifier = TelegramNotifier()
        print("✅ TelegramNotifier создан")

        print("✅ Отсутствующие модули обрабатываются корректно")
        return True

    except Exception as e:
        print(f"❌ Ошибка создания модулей: {e}")
        return False

if __name__ == "__main__":
    print("🚀 Запуск теста Фазы 3 (исправленная версия)")
    print("=" * 50)

    success1 = test_imports()
    success2 = test_ml_system_creation()
    success3 = test_data_operations()
    success4 = test_service_ml_integration()
    success5 = test_missing_modules()

    print("\n" + "=" * 50)
    if success1 and success2 and success3 and success4 and success5:
        print("🎉 ФАЗА 3 ЗАВЕРШЕНА УСПЕШНО!")
        print("📋 Можно переходить к Фазе 4 (веб-интерфейс)")
    else:
        print("💥 Есть проблемы в Фазе 3!")
        sys.exit(1)