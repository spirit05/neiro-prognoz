# api_data/check_service.py (ИСПРАВЛЕННАЯ РАБОЧАЯ ВЕРСИЯ)
#!/usr/bin/env python3
"""
Проверка статуса сервиса автообучения - РАБОЧАЯ ВЕРСИЯ
"""

import os
import sys
import json
from datetime import datetime

# Добавляем пути
PROJECT_PATH = '/opt/project'
sys.path.insert(0, PROJECT_PATH)
sys.path.insert(0, os.path.dirname(__file__))

def check_service():
    """Проверка статуса сервиса автообучения"""
    print("🔍 Проверка статуса сервиса автообучения...")
    
    try:
        from auto_learning_service import AutoLearningService
        
        service = AutoLearningService()
        
        print("\n📊 СТАТУС СЕРВИСА:")
        print(f"✅ Система инициализирована: {service.system is not None}")
        print(f"🎯 Модель обучена: {service.system.is_trained if service.system else False}")
        print(f"📅 Последний обработанный тираж: {service.last_processed_draw or 'Нет'}")
        print(f"🔧 Сервис активен: {service.service_active}")
        print(f"📈 Ошибок API подряд: {service.consecutive_api_errors}")
        
        # Проверяем статус модели через систему
        if service.system:
            system_status = service.system.get_status()
            print(f"📁 Групп в датасете: {system_status.get('dataset_size', 0)}")
            print(f"🔧 Тип модели: {system_status.get('model_type', 'N/A')}")
            print(f"🎯 Ансамбль доступен: {system_status.get('ensemble_info', {}).get('ensemble_available', False)}")
        
        # 🔧 ПРОВЕРКА АНАЛИТИКИ САМООБУЧЕНИЯ
        results_file = '/opt/project/data/learning_results.json'
        if os.path.exists(results_file):
            with open(results_file, 'r', encoding='utf-8') as f:
                results = json.load(f)
            
            if 'predictions_accuracy' in results:
                predictions_accuracy = results['predictions_accuracy']
                total_entries = len(predictions_accuracy)
                auto_entries = len([r for r in predictions_accuracy if r.get('service_type') == 'auto_learning'])
                web_entries = total_entries - auto_entries
                
                print(f"\n📈 АНАЛИТИКА САМООБУЧЕНИЯ:")
                print(f"📊 Всего обработок: {total_entries}")
                print(f"  🤖 Автосервис: {auto_entries}")
                print(f"  🌐 Веб-версия: {web_entries}")
                
                if predictions_accuracy:
                    last_result = predictions_accuracy[-1]
                    print(f"🎯 Последняя обработка: {last_result.get('actual_group', 'Нет данных')}")
                    print(f"🔧 Тип: {last_result.get('service_type', 'web')}")
                    print(f"✅ Успешно: {last_result.get('learning_success', 'N/A')}")
                    print(f"🎯 Совпадений: {last_result.get('matches_count', 0)}/4")
                    print(f"📊 Точность: {last_result.get('accuracy_score', 0)*100:.1f}%")
                    
                    if last_result.get('new_predictions_count'):
                        print(f"🔮 Новых прогнозов: {last_result.get('new_predictions_count')}")
                
                # Статистика точности
                if predictions_accuracy:
                    accuracy_scores = [r.get('accuracy_score', 0) for r in predictions_accuracy if 'accuracy_score' in r]
                    if accuracy_scores:
                        avg_accuracy = sum(accuracy_scores) / len(accuracy_scores)
                        best_accuracy = max(accuracy_scores)
                        
                        print(f"\n📊 СТАТИСТИКА ТОЧНОСТИ:")
                        print(f"🎯 Средняя точность: {avg_accuracy*100:.1f}%")
                        print(f"🏆 Лучшая точность: {best_accuracy*100:.1f}%")
                        print(f"📈 Успешных (>0.5): {len([a for a in accuracy_scores if a >= 0.5])}")
            
            elif isinstance(results, list):
                # Старая структура
                print(f"📈 Всего обработок (старая структура): {len(results)}")
                if results:
                    last_result = results[-1]
                    print(f"🎯 Последняя обработка: {last_result.get('draw')} - {last_result.get('combination')}")
        else:
            print("📝 Файл аналитики не найден")
        
        # Проверяем веб-версию
        try:
            result = os.popen('pgrep -f streamlit').read()
            web_running = len(result.strip()) > 0
            print(f"\n🌐 Веб-версия: {'✅ Запущена' if web_running else '❌ Не запущена'}")
        except:
            print(f"\n🌐 Веб-версия: ❌ Не удалось проверить")
        
        return True
        
    except Exception as e:
        print(f"❌ Ошибка проверки сервиса: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    check_service()
