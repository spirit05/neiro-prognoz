# test_ml_system.py
#!/usr/bin/env python3
"""
Тест ML системы
"""

import sys
import os

PROJECT_ROOT = '/home/spirit/Desktop/project'
sys.path.insert(0, PROJECT_ROOT)

def test_ml_system():
    """Тестируем ML систему детально"""
    print("🔍 Детальное тестирование ML системы...")
    
    try:
        from ml.core.system import SimpleNeuralSystem
        
        # Создаем систему
        system = SimpleNeuralSystem()
        print("✅ SimpleNeuralSystem создан")
        
        # Проверяем методы
        methods = ['get_status', 'train', 'predict', 'add_data_and_retrain']
        for method in methods:
            if hasattr(system, method):
                print(f"✅ Метод {method} существует")
            else:
                print(f"❌ Метод {method} отсутствует")
        
        # Тестируем get_status
        if hasattr(system, 'get_status'):
            status = system.get_status()
            print(f"✅ get_status() работает: {status}")
            return True
        else:
            print("❌ get_status() отсутствует")
            return False
            
    except Exception as e:
        print(f"❌ Ошибка в ML системе: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = test_ml_system()
    sys.exit(0 if success else 1)
    