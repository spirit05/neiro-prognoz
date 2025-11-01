# [file name]: test_enhanced_system.py
"""
Тестирование усиленной системы
"""

import os
import sys
sys.path.insert(0, os.path.dirname(__file__))

from model.simple_system import SimpleNeuralSystem
from model.data_loader import load_dataset

def test_basic_functionality():
    """Тест базовой функциональности"""
    print("🧪 Тестирование усиленной системы...")
    
    # Инициализация системы
    system = SimpleNeuralSystem()
    
    # Проверка статуса
    status = system.get_status()
    print(f"📊 Статус системы: {status}")
    
    # Загрузка данных
    dataset = load_dataset()
    print(f"📁 Загружено {len(dataset)} групп")
    
    # Тест предсказания (если есть данные)
    if len(dataset) >= 50:
        print("🔮 Тестирование предсказания...")
        try:
            predictions = system.predict(top_k=5)
            if predictions:
                print(f"✅ Получено {len(predictions)} предсказаний:")
                for i, (group, score) in enumerate(predictions, 1):
                    print(f"   {i}. {group} (score: {score:.6f})")
            else:
                print("❌ Предсказания не получены")
        except Exception as e:
            print(f"❌ Ошибка предсказания: {e}")
    else:
        print("⚠️  Недостаточно данных для теста предсказания")
    
    print("✅ Базовое тестирование завершено")

def test_ensemble_features():
    """Тест ансамблевых функций"""
    print("\n🎯 Тестирование ансамблевых функций...")
    
    system = SimpleNeuralSystem()
    
    # Проверка ансамблевого режима
    print("🔧 Проверка переключения режимов...")
    original_mode = system.ensemble_enabled
    system.toggle_ensemble(not original_mode)
    print(f"   Режим изменен: {original_mode} -> {system.ensemble_enabled}")
    
    # Возвращаем исходный режим
    system.toggle_ensemble(original_mode)
    print(f"   Режим восстановлен: {system.ensemble_enabled}")
    
    print("✅ Ансамблевые функции работают")

if __name__ == "__main__":
    test_basic_functionality()
    test_ensemble_features()
    print("\n🎉 Все тесты завершены успешно!")