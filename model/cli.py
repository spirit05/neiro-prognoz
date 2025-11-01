# [file name]: model/cli.py (ОСТАЛСЯ БЕЗ ИЗМЕНЕНИЙ)
"""
Главный CLI интерфейс для УСИЛЕННОЙ нейросети
"""

import os
import sys
from typing import List, Tuple

# Добавляем родительскую директорию в путь для импортов
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

# Правильные импорты
from model.data_loader import load_dataset, save_dataset, validate_group, compare_groups, save_predictions, load_predictions
from model.simple_system import SimpleNeuralSystem

# Глобальная переменная для системы
system = None

def get_system():
    """Получаем или создаем систему"""
    global system
    if system is None:
        system = SimpleNeuralSystem()
    return system

def show_last_group() -> str:
    """Вернуть последнюю группу"""
    dataset = load_dataset()
    if not dataset:
        print("📭 Датасет пуст")
        return
    
    return dataset[-1]

def show_last_groups(n: int = 5) -> None:
    """Показать последние группы"""
    dataset = load_dataset()
    if not dataset:
        print("📭 Датасет пуст")
        return
    
    print(f"\n📋 Последние {n} групп:")
    for i, group in enumerate(dataset[-n:], 1):
        print(f"  {i}) {group}")
    print(f"Всего групп: {len(dataset)}")

def check_similarity(new_group_str: str) -> None:
    """Проверить совпадение с последними предсказаниями"""
    predictions = load_predictions()
    if not predictions:
        print("📊 Нет предыдущих предсказаний для сравнения")
        return
    
    try:
        new_numbers = [int(x) for x in new_group_str.strip().split()]
        new_group = tuple(new_numbers)
        
        matches_found = []
        
        for pred_group, score in predictions:
            comparison = compare_groups(pred_group, new_group)
            if comparison['total_matches'] > 0:
                matches_found.append((pred_group, comparison))
        
        if matches_found:
            print(f"🔍 Найдено совпадений с {len(matches_found)} предсказаниями:")
            for i, (pred_group, comparison) in enumerate(matches_found[:3], 1):
                print(f"  {i}) Предсказание: {pred_group[0]} {pred_group[1]} {pred_group[2]} {pred_group[3]}")
                print(f"     Совпадения по парам: {comparison['total_matches']}/4")
                print(f"     Точные совпадения: {comparison['exact_matches']}/4")
        else:
            print("📝 Совпадений с предыдущими прогнозами нет")
            
    except Exception as e:
        print(f"❌ Ошибка при сравнении: {e}")

def add_new_group() -> None:
    """Добавить новую группу с дообучением УСИЛЕННОЙ модели и прогнозом"""
    print("\n➕ Добавление новой группы")
    group_input = input(f"(последняя: '{show_last_group()}'): ").strip()
    
    if not group_input:
        print("❌ Пустой ввод")
        return
    
    if not validate_group(group_input):
        print("❌ Неверный формат группы. Должно быть 4 числа 1-26, в парах числа не должны совпадать")
        return
    
    system = get_system()
    
    # Проверяем совпадения перед добавлением
    check_similarity(group_input)
    
    # Добавляем и дообучаем
    print("\n🔄 Обработка данных УСИЛЕННОЙ моделью...")
    predictions = system.add_data_and_retrain(group_input, 7)
    
    # Показываем прогноз после дообучения
    if predictions:
        print(f"\n🎯 НОВЫЕ ПРОГНОЗЫ после добавления данных:")
        for i, (group, score) in enumerate(predictions, 1):
            confidence = "🟢 ВЫСОКАЯ" if score > 0.01 else "🟡 СРЕДНЯЯ" if score > 0.001 else "🔴 НИЗКАЯ"
            print(f"  {i}) {group[0]} {group[1]} {group[2]} {group[3]} (score: {score:.6f}) {confidence}")
        
        # Сохраняем новые предсказания
        save_predictions(predictions)
        print(f"💾 Новые предсказания сохранены")
        
        # # Сравниваем новую группу с новыми прогнозами
        # print(f"\n🔍 Сравнение новой группы с новыми прогнозами:")
        # new_numbers = [int(x) for x in group_input.strip().split()]
        # new_group = tuple(new_numbers)
        
        # best_match = None
        # best_score = 0
        # for pred_group, score in predictions[:3]:  # Проверяем топ-3 прогноза
        #     comparison = compare_groups(pred_group, new_group)
        #     if comparison['total_matches'] > best_score:
        #         best_score = comparison['total_matches']
        #         best_match = (pred_group, comparison)
        
        # if best_match and best_score > 0:
        #     pred_group, comparison = best_match
        #     print(f"✅ Лучшее совпадение: {pred_group[0]} {pred_group[1]} {pred_group[2]} {pred_group[3]}")
        #     print(f"   Совпадения по парам: {comparison['total_matches']}/4")
        #     print(f"   Точные совпадения: {comparison['exact_matches']}/4")
            
        #     if comparison['total_matches'] >= 2:
        #         print("🎉 ОТЛИЧНОЕ СОВПАДЕНИЕ!")
        #     elif comparison['total_matches'] == 1:
        #         print("👍 ХОРОШЕЕ СОВПАДЕНИЕ!")
        # else:
        #     print("📝 Совпадений с новыми прогнозами нет")
    else:
        print("❌ Не удалось получить прогнозы после добавления данных")

def train_simple_neural() -> None:
    """Обучить УСИЛЕННУЮ нейросеть с прогнозом после обучения"""
    print("\n🧠 Обучение УСИЛЕННОЙ нейросети")
    
    system = get_system()
    predictions = system.train(epochs=25)
    
    # Показываем прогноз после обучения
    if predictions:
        print(f"\n🎯 ПРОГНОЗЫ после обучения УСИЛЕННОЙ модели:")
        for i, (group, score) in enumerate(predictions, 1):
            confidence = "🟢 ВЫСОКАЯ" if score > 0.01 else "🟡 СРЕДНЯЯ" if score > 0.001 else "🔴 НИЗКАЯ"
            print(f"  {i}) {group[0]} {group[1]} {group[2]} {group[3]} (score: {score:.6f}) {confidence}")
        
        # Сохраняем предсказания
        save_predictions(predictions)
        print(f"💾 Прогнозы сохранены для сравнения")
    else:
        print("❌ Не удалось получить прогнозы после обучения")

def predict_with_simple_neural() -> None:
    """Предсказание УСИЛЕННОЙ нейросетью"""
    print("\n🔮 Предсказание УСИЛЕННОЙ нейросетью")
    
    system = get_system()
    predictions = system.predict(top_k=10)
    
    if predictions:
        print(f"\n🏆 TOP-{len(predictions)} прогнозов УСИЛЕННОЙ модели:")
        for i, (group, score) in enumerate(predictions, 1):
            confidence = "🟢 ВЫСОКАЯ" if score > 0.01 else "🟡 СРЕДНЯЯ" if score > 0.001 else "🔴 НИЗКАЯ"
            print(f"  {i}) {group[0]} {group[1]} {group[2]} {group[3]} (score: {score:.6f}) {confidence}")
        
        # Сохраняем предсказания для будущего сравнения
        save_predictions(predictions)
        print(f"💾 {len(predictions)} предсказаний сохранены для сравнения")
    else:
        print("❌ Нейросеть не смогла сделать предсказание")

def show_system_status() -> None:
    """Показать статус системы"""
    print("\n🔧 Статус системы")
    
    system = get_system()
    status = system.get_status()
    dataset = load_dataset()
    
    print(f"📊 Групп в датасете: {len(dataset)}")
    print(f"📈 Достаточно данных: {'✅ Да' if status['has_sufficient_data'] else '❌ Нет (нужно минимум 50)'}")
    print(f"🧠 Нейросеть обучена: {'✅ Да' if status['is_trained'] else '❌ Нет'}")
    print(f"💾 Модель загружена: {'✅ Да' if status['model_loaded'] else '❌ Нет'}")
    print(f"🚀 Тип модели: {status.get('model_type', 'УСИЛЕННАЯ')}")
    print(f"📁 Путь к модели: {status['model_path']}")
    
    # Показываем последние предсказания
    predictions = load_predictions()
    if predictions:
        print(f"📈 Последние предсказания: {len(predictions)}")
        print("   Топ-3 последних предсказания:")
        for i, (group, score) in enumerate(predictions[:3], 1):
            confidence = "🟢" if score > 0.01 else "🟡" if score > 0.001 else "🔴"
            print(f"     {i}) {group[0]} {group[1]} {group[2]} {group[3]} (score: {score:.6f}) {confidence}")
    else:
        print("📈 Последние предсказания: нет")

def main_menu() -> None:
    """Главное меню"""
    # Инициализируем систему при запуске
    get_system()
    
    while True:
        print("\n" + "="*50)
        print("          🎯 УСИЛЕННАЯ НЕЙРОСЕТЬ v3.0")
        print("="*50)
        print("1) 📋 Показать последние группы")
        print("2) ➕ Добавить новую группу (с дообучением и прогнозом)")
        print("3) 🧠 Обучить УСИЛЕННУЮ нейросеть (с прогнозом)")
        print("4) 🔮 Получить прогноз от УСИЛЕННОЙ модели")
        print("5) 🔧 Статус системы") 
        print("0) 🚪 Выход")
        print("-"*50)
        
        choice = input("Выберите пункт: ").strip()
        
        if choice == "1":
            show_last_groups()
        elif choice == "2":
            add_new_group()
        elif choice == "3":
            train_simple_neural()
        elif choice == "4":
            predict_with_simple_neural()
        elif choice == "5":
            show_system_status()
        elif choice == "0":
            print("👋 До свидания!")
            break
        else:
            print("❌ Неверный выбор")
        

if __name__ == "__main__":
    # Создаем необходимые директории
    os.makedirs('data', exist_ok=True)
    
    print("🚀 Запуск УСИЛЕННОЙ нейросети для предсказания чисел...")
    print("   Теперь с улучшенной архитектурой и интеллектуальными прогнозами! 🎯")
    main_menu()