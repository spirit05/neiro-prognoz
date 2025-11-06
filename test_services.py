# test_services.py
#!/usr/bin/env python3
"""
Тест сервисов
"""

import sys
import os

PROJECT_ROOT = '/home/spirit/Desktop/project'
sys.path.insert(0, PROJECT_ROOT)

def test_services():
    """Тестируем сервисы детально"""
    print("🔍 Детальное тестирование сервисов...")
    
    try:
        # Проверим импорт логгера
        from utils.logging_system import get_AutoLearningService_logger
        print("✅ get_AutoLearningService_logger импортируется")
        
        # Проверим сервис
        from services.auto_learning.service import AutoLearningService
        print("✅ AutoLearningService импортируется")
        
        service = AutoLearningService()
        print("✅ AutoLearningService создан")
        
        status = service.get_service_status()
        print(f"✅ get_service_status() работает: {status}")
        
        return True
        
    except Exception as e:
        print(f"❌ Ошибка в сервисах: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = test_services()
    sys.exit(0 if success else 1)