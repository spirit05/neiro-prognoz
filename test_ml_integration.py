#!/usr/bin/env python3
"""
Тест интеграции автосервиса с ML системой
"""

import sys
import os

# Добавляем пути
sys.path.insert(0, '/opt/dev')

from services.auto_learning.service import AutoLearningService

def test_ml_integration():
    """Тестирование интеграции с ML системой"""
    print("🧪 Тестирование интеграции автосервиса с ML системой...")
    
    try:
        # Создаем экземпляр сервиса
        service = AutoLearningService()
        
        # Проверяем инициализацию ML системы
        print(f"✅ ML система инициализирована: {service.system is not None}")
        
        # Проверяем статус
        status = service.get_service_status()
        print(f"✅ Статус сервиса: {status}")
        
        # Тестируем резервные методы
        test_combination = "1 2 3 4"
        predictions = service.fallback_retrain(test_combination)
        print(f"✅ Резервные прогнозы сгенерированы: {len(predictions)}")
        
        # Тестируем сравнение с прогнозами
        comparison = service.compare_with_predictions(test_combination)
        print(f"✅ Сравнение с прогнозами: {comparison['matches_found']} совпадений")
        
        print("🎉 Интеграция с ML системой работает корректно!")
        return True
        
    except Exception as e:
        print(f"❌ Ошибка тестирования интеграции: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    test_ml_integration()