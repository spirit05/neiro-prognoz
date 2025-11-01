# [file name]: model/cli.py (ОБНОВЛЕННЫЙ ДЛЯ САМООБУЧЕНИЯ)
"""
Главный CLI интерфейс для УСИЛЕННОЙ нейросети с самообучением
"""

import os
import sys
import logging
from typing import List, Tuple

# Настройка логирования
logger = logging.getLogger('SequencePredictor')

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
        return ""
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

def show_learning_insights() -> None:
    """Показать аналитику самообучения"""
    print("\n📈 Аналитика самообучения системы")
    
    system = get_system()
    insights = system.get_learning_insights()
    
    if isinstance(insights, dict):
        if 'message' in insights:
            print(f"   {insights['message']}")
        else:
            print(f"   📊 Проанализировано предсказаний: {insights.get('total_predictions_analyzed', 0)}")
            accuracy = insights.get('recent_accuracy_avg', 0)
            print(f"   🎯 Средняя точность: {accuracy:.1%}")
            print(f"   🏆 Лучшая точность: {insights.get('best_accuracy', 0):.1%}")
            
            recommendations = insights.get('recommendations', [])
            if recommendations:
                print("   💡 Рекомендации:")
                for rec in recommendations:
                    print(f"      • {rec}")
    else:
        print("   📊 Собираем данные для анализа...")

def add_new_group() -> None:
    """Добавить новую группу с дообучением УСИЛЕННОЙ модели и прогнозом"""
    print("\n➕ Добавление новой группы")
    last_group = show_last_group()
    if last_group:
        group_input = input(f"(последняя: '{last_group}'): ").strip()
    else:
        group_input = input("Введите 4 числа через пробел: ").strip()
    
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
        
        # Показываем аналитику самообучения
        show_learning_insights()
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
        
        # Показываем аналитику
        show_learning_insights()
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
    
    # Информация об ансамбле
    ensemble_info = status.get('ensemble_info', {})
    print(f"🔧 Ансамблевый режим: {'✅ Включен' if ensemble_info.get('ensemble_enabled', False) else '❌ Выключен'}")
    print(f"🎯 Компонентов ансамбля: {ensemble_info.get('ensemble_components', 0)}")
    
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
    
    # Показываем аналитику самообучения
    show_learning_insights()

def advanced_controls() -> None:
    """Расширенные настройки системы"""
    print("\n🔧 Расширенные настройки")
    
    system = get_system()
    
    while True:
        print("\n" + "-"*30)
        print("1) 🔄 Обновить ансамблевую систему")
        print("2) ⚙️  Переключить ансамблевый режим")
        print("3) 🗑️  Сбросить данные самообучения")
        print("4) 📊 Детальная статистика")
        print("0) ↩️  Назад")
        print("-"*30)
        
        choice = input("Выберите пункт: ").strip()
        
        if choice == "1":
            try:
                system._update_full_ensemble()
                print("✅ Ансамблевая система обновлена!")
            except Exception as e:
                print(f"❌ Ошибка: {e}")
                
        elif choice == "2":
            current_mode = system.ensemble_enabled
            new_mode = not current_mode
            system.toggle_ensemble(new_mode)
            status = "включен" if new_mode else "выключен"
            print(f"✅ Ансамблевый режим {status}")
            
        elif choice == "3":
            confirm = input("⚠️  Вы уверены? Это удалит всю историю самообучения. (y/N): ").strip().lower()
            if confirm == 'y':
                system.reset_learning_data()
                print("✅ Данные самообучения сброшены!")
            else:
                print("❌ Отменено")
                
        elif choice == "4":
            status = system.get_status()
            print("\n📊 Детальная статистика:")
            import json
            print(json.dumps(status, indent=2, ensure_ascii=False))
            
        elif choice == "0":
            break
        else:
            print("❌ Неверный выбор")

def main_menu() -> None:
    """Главное меню"""
    # Инициализируем систему при запуске
    get_system()
    
    while True:
        print("\n" + "="*50)
        print("          🎯 УСИЛЕННАЯ НЕЙРОСЕТЬ v4.0")
        print("           с САМООБУЧЕНИЕМ и АНСАМБЛЕМ")
        print("="*50)
        print("1) 📋 Показать последние группы")
        print("2) ➕ Добавить новую группу (с дообучением и прогнозом)")
        print("3) 🧠 Обучить УСИЛЕННУЮ нейросеть (с прогнозом)")
        print("4) 🔮 Получить прогноз от УСИЛЕННОЙ модели")
        print("5) 🔧 Статус системы")
        print("6) ⚙️  Расширенные настройки")
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
        elif choice == "6":
            advanced_controls()
        elif choice == "0":
            print("👋 До свидания!")
            break
        else:
            print("❌ Неверный выбор")

if __name__ == "__main__":
    # Создаем необходимые директории
    os.makedirs('data', exist_ok=True)
    
    print("🚀 Запуск УСИЛЕННОЙ нейросети для предсказания чисел...")
    print("   Теперь с самообучением и улучшенной точностью! 🎯")
    main_menu()