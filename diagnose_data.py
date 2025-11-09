#!/usr/bin/env python3
"""
Диагностика структуры данных системы
"""

import os
import json
import sys
from pathlib import Path

PROJECT_ROOT = '/opt/dev'
sys.path.insert(0, PROJECT_ROOT)

def diagnose_data_structure():
    """Диагностика структуры всех данных"""
    print("🔍 ДИАГНОСТИКА СТРУКТУРЫ ДАННЫХ\n")
    
    # Проверяем learning_results.json
    learning_file = Path(PROJECT_ROOT) / 'data' / 'analytics' / 'learning_results.json'
    if learning_file.exists():
        try:
            with open(learning_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            print(f"📊 learning_results.json:")
            print(f"   Тип: {type(data)}")
            print(f"   Размер: {len(data) if isinstance(data, (list, dict)) else 'N/A'}")
            
            if isinstance(data, dict):
                print("   Структура словаря:")
                for key, value in data.items():
                    print(f"     {key}: {type(value)} (размер: {len(value) if isinstance(value, (list, dict)) else 'N/A'})")
            elif isinstance(data, list):
                print("   Первые 3 элемента списка:")
                for i, item in enumerate(data[:3]):
                    print(f"     [{i}]: {type(item)} - {str(item)[:100]}...")
            
        except Exception as e:
            print(f"   ❌ Ошибка чтения: {e}")
    else:
        print("❌ Файл learning_results.json не найден")
    
    print("\n" + "="*50)
    
    # Проверяем другие критические файлы
    critical_files = [
        'data/analytics/info.json',
        'data/analytics/predictions_state.json', 
        'data/analytics/service_state.json',
        'data/datasets/dataset.json'
    ]
    
    for file_path in critical_files:
        full_path = Path(PROJECT_ROOT) / file_path
        if full_path.exists():
            try:
                with open(full_path, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                print(f"✅ {file_path}: {type(data)}")
            except Exception as e:
                print(f"❌ {file_path}: Ошибка - {e}")
        else:
            print(f"⚠️  {file_path}: Не найден")

if __name__ == "__main__":
    diagnose_data_structure()
