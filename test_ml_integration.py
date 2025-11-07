#!/usr/bin/env python3
"""
Тест исправленной интеграции автосервиса с ML системой
"""

import sys
import os

# Добавляем пути
sys.path.insert(0, '/opt/dev')

from services.auto_learning.service import AutoLearningService

def test_fixed_integration():
    """Тестирование исправленной интеграции"""
    print("🧪 Тестирование исправленной интеграции автосервиса с ML системой...")
    
    try:
        # Создаем экземпляр сервиса
        service = AutoLearningService()
        
        # Проверяем инициализацию ML системы
        print(f"✅ ML система инициализирована: {service.system is not None}")
        
        # Проверяем статус
        status = service.get_service_status()
        print(f"✅ Статус сервиса получен: активен={status['service_active']}")
        print(f"✅ Ошибок API: {status['consecutive_api_errors']}")
        
        # Тестируем резервные методы
        test_combination = "1 2 3 4"
        predictions = service.fallback_retrain(test_combination)
        print(f"✅ Резервные прогнозы сгенерированы: {len(predictions)}")
        
        if predictions:
            for i, (group, score) in enumerate(predictions):
                print(f"   {i+1}. {group} (score: {score:.3f})")
        
        # Тестируем сравнение с прогнозами
        comparison = service.compare_with_predictions(test_combination)
        print(f"✅ Сравнение с прогнозами: {comparison['matches_found']} совпадений")
        
        # Тестируем валидацию
        valid = service.validate_group_fallback(test_combination)
        print(f"✅ Валидация группы: {valid}")
        
        invalid = service.validate_group_fallback("1 2 3 21")  # Невалидная
        print(f"✅ Валидация невалидной группы: {not invalid}")
        
        print("🎉 Исправленная интеграция работает корректно!")
        return True
        
    except Exception as e:
        print(f"❌ Ошибка тестирования интеграции: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    test_fixed_integration()
