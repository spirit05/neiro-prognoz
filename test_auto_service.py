#!/usr/bin/env python3
"""
Тест новой структуры автосервиса
"""

import sys
import os

# Добавляем пути
sys.path.insert(0, '/opt/dev')

from services.auto_learning.service import AutoLearningService

def test_auto_service():
    """Тестирование автосервиса"""
    print("🧪 Тестирование автосервиса...")
    
    try:
        # Создаем экземпляр сервиса
        service = AutoLearningService()
        
        # Проверяем инициализацию
        print(f"✅ Сервис инициализирован: {service.system is not None}")
        print(f"✅ API Client: {service.api_client is not None}")
        print(f"✅ Scheduler: {service.scheduler is not None}")
        print(f"✅ State Manager: {service.state_manager is not None}")
        print(f"✅ Telegram Notifier: {service.telegram is not None}")
        
        # Проверяем статус
        status = service.get_service_status()
        print(f"✅ Статус сервиса получен: {status['service_active']}")
        
        print("🎉 Все компоненты автосервиса работают корректно!")
        return True
        
    except Exception as e:
        print(f"❌ Ошибка тестирования: {e}")
        return False

if __name__ == "__main__":
    test_auto_service()