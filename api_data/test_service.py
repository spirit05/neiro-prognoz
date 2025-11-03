# api_data/test_service.py
#!/usr/bin/env python3
"""
Тестирование сервиса автообучения
"""

import os
import sys

# Добавляем пути
PROJECT_PATH = '/opt/project'
sys.path.insert(0, PROJECT_PATH)
sys.path.insert(0, os.path.dirname(__file__))

from auto_learning_service import AutoLearningService

def test_service():
    """Тестирование сервиса"""
    print("🧪 Тестирование сервиса автообучения...")
    
    try:
        # Тест 1: Инициализация
        print("1. Инициализация системы...")
        service = AutoLearningService()
        if service.system:
            print("   ✅ Система инициализирована")
        else:
            print("   ❌ Ошибка инициализации")
            return False
        
        # Тест 2: Получение статуса
        print("2. Проверка статуса...")
        status = service.get_service_status()
        print(f"   ✅ Статус получен: модель обучена = {status.get('model_trained', False)}")
        
        # Тест 3: Расчет времени следующего запуска
        print("3. Расчет времени следующего запуска...")
        next_interval = service.calculate_next_run_time()
        print(f"   ✅ Следующий запуск через: {next_interval:.1f} минут")
        
        # Тест 4: Тест Telegram (если настроено)
        print("4. Тест Telegram уведомлений...")
        service.telegram.send_message("🧪 <b>ТЕСТ СЕРВИСА</b>\nСервис автообучения успешно прошел тесты")
        print("   ✅ Тест Telegram выполнен")
        
        print("\n🎉 Все тесты пройдены успешно!")
        return True
        
    except Exception as e:
        print(f"   ❌ Ошибка тестирования: {e}")
        return False

if __name__ == "__main__":
    success = test_service()
    if success:
        print("\n🎉 Все тесты пройдены успешно!")
    else:
        print("\n💥 Тесты завершились с ошибками!")
        sys.exit(1)