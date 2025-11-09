#!/usr/bin/env python3
"""
Безопасная миграция данных между версиями
"""

import os
import json
import shutil
from datetime import datetime
from pathlib import Path

PROJECT_ROOT = '/opt/dev'

def create_backup(file_path):
    """Создание резервной копии файла"""
    backup_path = file_path.with_suffix(f'.backup.{datetime.now().strftime("%Y%m%d_%H%M%S")}')
    shutil.copy2(file_path, backup_path)
    return backup_path

def migrate_learning_results():
    """Миграция learning_results.json с сохранением данных"""
    learning_file = Path(PROJECT_ROOT) / 'data' / 'analytics' / 'learning_results.json'
    
    if not learning_file.exists():
        print("❌ Файл learning_results.json не найден")
        return False
    
    # Создаем резервную копию
    backup_path = create_backup(learning_file)
    print(f"💾 Создана резервная копия: {backup_path}")
    
    try:
        with open(learning_file, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        print(f"📊 Текущий формат: {type(data)}")
        
        if isinstance(data, list):
            print("🔄 Миграция: список -> словарь")
            migrated_data = {
                'predictions_accuracy': data,  # Сохраняем все старые данные
                'model_performance': {},
                'learning_patterns': {},
                'error_patterns': [],
                'last_analysis': None,
                'migration_info': {
                    'migrated_from': 'list',
                    'migration_date': datetime.now().isoformat(),
                    'original_count': len(data)
                }
            }
            
            with open(learning_file, 'w', encoding='utf-8') as f:
                json.dump(migrated_data, f, ensure_ascii=False, indent=2)
            
            print("✅ Миграция learning_results.json завершена")
            return True
            
        elif isinstance(data, dict):
            print("✅ learning_results.json уже в правильном формате")
            return True
        else:
            print(f"❌ Неизвестный формат: {type(data)}")
            return False
            
    except Exception as e:
        print(f"❌ Ошибка миграции: {e}")
        print(f"💡 Восстановите из резервной копии: cp {backup_path} {learning_file}")
        return False

def safe_migration():
    """Безопасная миграция всех данных"""
    print("🚀 ЗАПУСК БЕЗОПАСНОЙ МИГРАЦИИ ДАННЫХ\n")
    
    # Мигрируем только learning_results.json
    success = migrate_learning_results()
    
    print("\n" + "="*50)
    if success:
        print("🎯 МИГРАЦИЯ ЗАВЕРШЕНА УСПЕШНО")
        print("💡 Теперь можно запускать систему")
    else:
        print("💥 МИГРАЦИЯ НЕ УДАЛАСЯ")
        print("💡 Система осталась в исходном состоянии")
    
    return success

if __name__ == "__main__":
    safe_migration()
