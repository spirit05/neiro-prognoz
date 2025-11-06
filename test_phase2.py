# test_phase2.py
#!/usr/bin/env python3
"""
Тест Фазы 2 - рефакторинг auto_learning_service.py
"""

import sys
import os

PROJECT_ROOT = '/home/spirit/Desktop/project'
sys.path.insert(0, PROJECT_ROOT)

def test_imports():
    """Тестируем импорты новых модулей"""
    print("🧪 Тестируем импорты Фазы 2...")
    
    try:
        # Тестируем файловый менеджер
        from services.auto_learning.file_manager import FileLock, safe_file_operation
        print("✅ FileManager импортируется")
        
        # Тестируем scheduler
        from services.auto_learning.scheduler import SmartScheduler
        scheduler = SmartScheduler()
        print("✅ Scheduler импортируется")
        
        # Тестируем API клиент
        from services.auto_learning.api_client import APIClient
        api_client = APIClient()
        print("✅ APIClient импортируется")
        
        # Тестируем основной сервис
        from services.auto_learning.service import AutoLearningService
        print("✅ AutoLearningService импортируется")
        
        # Тестируем Telegram notifier
        from services.telegram.notifier import TelegramNotifier
        notifier = TelegramNotifier()
        print("✅ TelegramNotifier импортируется")
        
        print("🎉 Все модули Фазы 2 импортируются корректно!")
        return True
        
    except Exception as e:
        print(f"❌ Ошибка импорта: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_service_creation():
    """Тестируем создание сервиса"""
    print("\n🔧 Тестируем создание сервиса...")
    
    try:
        from services.auto_learning.service import AutoLearningService
        
        # Создаем сервис (без реальной инициализации системы)
        service = AutoLearningService()
        
        # Проверяем основные атрибуты
        assert hasattr(service, 'service_active'), "Сервис должен иметь атрибут service_active"
        assert hasattr(service, 'scheduler'), "Сервис должен иметь атрибут scheduler"
        assert hasattr(service, 'api_client'), "Сервис должен иметь атрибут api_client"
        assert hasattr(service, 'telegram'), "Сервис должен иметь атрибут telegram"
        
        print("✅ Сервис создается корректно")
        return True
        
    except Exception as e:
        print(f"❌ Ошибка создания сервиса: {e}")
        return False

def test_scheduler_logic():
    """Тестируем логику расписания"""
    print("\n⏰ Тестируем логику расписания...")
    
    try:
        from services.auto_learning.scheduler import SmartScheduler
        from datetime import datetime
        
        scheduler = SmartScheduler()
        
        # Тестируем расчет времени
        test_time = datetime(2024, 1, 1, 12, 0, 0)  # 12:00
        interval, interval_type = scheduler.calculate_next_run_time(test_time)
        
        print(f"📅 Интервал: {interval}, тип: {interval_type}")
        print("✅ Логика расписания работает")
        return True
        
    except Exception as e:
        print(f"❌ Ошибка логики расписания: {e}")
        return False

if __name__ == "__main__":
    print("🚀 Запуск теста Фазы 2")
    print("=" * 50)
    
    success1 = test_imports()
    success2 = test_service_creation()
    success3 = test_scheduler_logic()
    
    print("\n" + "=" * 50)
    if success1 and success2 and success3:
        print("🎉 ФАЗА 2 ЗАВЕРШЕНА УСПЕШНО!")
        print("📋 Следующий шаг: Фаза 3 - интеграция и тестирование")
    else:
        print("💥 Есть проблемы в Фазе 2!")
        sys.exit(1)