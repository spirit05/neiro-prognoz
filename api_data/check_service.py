# api_data/check_service.py
#!/usr/bin/env python3
"""
Проверка статуса сервиса автообучения
"""

import os
import sys
import json
from datetime import datetime

# Добавляем пути
PROJECT_PATH = '/opt/project'
sys.path.insert(0, PROJECT_PATH)
sys.path.insert(0, os.path.dirname(__file__))

from auto_learning_service import AutoLearningService

def check_service():
    """Проверка статуса сервиса"""
    print("🔍 Проверка статуса сервиса автообучения...")
    
    try:
        service = AutoLearningService()
        status = service.get_service_status()
        
        print("\n📊 СТАТУС СЕРВИСА:")
        print(f"✅ Система инициализирована: {status['system_initialized']}")
        print(f"🎯 Модель обучена: {status.get('model_trained', False)}")
        print(f"📅 Последний обработанный тираж: {status.get('last_processed_draw', 'Нет')}")
        print(f"🕐 Время проверки: {status['timestamp']}")
        
        if status.get('dataset_size'):
            print(f"📁 Групп в датасете: {status['dataset_size']}")
        
        if status.get('ensemble_info'):
            ensemble = status['ensemble_info']
            print(f"🔧 Ансамбль доступен: {ensemble.get('ensemble_available', False)}")
        
        # Проверяем результаты обучения
        results_file = os.path.join(os.path.dirname(__file__), 'learning_results.json')
        if os.path.exists(results_file):
            with open(results_file, 'r', encoding='utf-8') as f:
                results = json.load(f)
            print(f"📈 Всего обработок: {len(results)}")
            
            if results:
                last_result = results[-1]
                print(f"🎯 Последняя обработка: {last_result.get('draw')} - {last_result.get('combination')}")
                print(f"✅ Успешно: {last_result.get('learning_success', False)}")
                print(f"🔮 Новых прогнозов: {last_result.get('new_predictions_count', 0)}")
        
        return True
        
    except Exception as e:
        print(f"❌ Ошибка проверки сервиса: {e}")
        return False

if __name__ == "__main__":
    check_service()