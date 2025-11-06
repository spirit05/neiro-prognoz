# fix_log_paths.py
#!/usr/bin/env python3
"""
Скрипт для исправления всех путей к логам в проекте
"""

import os
import re

PROJECT_ROOT = '/home/spirit/Desktop/project'

def fix_log_paths_in_file(file_path):
    """Исправляет пути к логам в одном файле"""
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    original_content = content
    
    # Заменяем старые пути к логам на новые
    replacements = {
        r"paths.TRAINING_LOG": "paths.TRAINING_LOG",
        r'paths.TRAINING_LOG': "paths.TRAINING_LOG",
        r"paths.TRAINING_LOG": "paths.TRAINING_LOG", 
        r'paths.TRAINING_LOG': "paths.TRAINING_LOG",
        r"paths.AUTO_LEARNING_LOG": "paths.AUTO_LEARNING_LOG",
        r'paths.AUTO_LEARNING_LOG': "paths.AUTO_LEARNING_LOG",
        r"logging\.getLogger\('([^']+)'\)": r"get_\1_logger()"
    }
    
    for old, new in replacements.items():
        content = re.sub(old, new, content)
    
    # Добавляем импорт если нужно
    if 'paths.TRAINING_LOG' in content and 'from config.paths import paths' not in content:
        # Находим место для импорта (после других импортов)
        lines = content.split('\n')
        insert_index = 0
        for i, line in enumerate(lines):
            if line.startswith('import ') or line.startswith('from '):
                insert_index = i + 1
            elif line.strip() and not line.startswith(('import ', 'from ', '#', '"', "'")):
                break
        
        # Добавляем импорт
        lines.insert(insert_index, 'from config.paths import paths')
        content = '\n'.join(lines)
    
    # Добавляем импорт для новых логгеров если нужно
    if 'get_' in content and 'logger()' in content and 'from utils.logging_system import' not in content:
        lines = content.split('\n')
        insert_index = 0
        for i, line in enumerate(lines):
            if line.startswith('import ') or line.startswith('from '):
                insert_index = i + 1
            elif line.strip() and not line.startswith(('import ', 'from ', '#', '"', "'")):
                break
        
        # Добавляем импорт
        lines.insert(insert_index, 'from utils.logging_system import get_training_logger, get_ml_system_logger, get_auto_learning_logger')
        content = '\n'.join(lines)
    
    if content != original_content:
        print(f"🔧 Исправлен: {file_path}")
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(content)
        return True
    
    return False

def main():
    """Основная функция"""
    print("🔧 Исправление путей к логам во всем проекте...")
    
    fixed_files = []
    
    # Обходим все Python файлы в проекте
    for root, dirs, files in os.walk(PROJECT_ROOT):
        # Пропускаем виртуальное окружение и служебные директории
        if any(skip in root for skip in ['env', '__pycache__', '.git', 'node_modules']):
            continue
            
        for file in files:
            if file.endswith('.py'):
                file_path = os.path.join(root, file)
                if fix_log_paths_in_file(file_path):
                    fixed_files.append(file_path)
    
    print(f"\n✅ Исправлено файлов: {len(fixed_files)}")
    for file in fixed_files:
        print(f"   📝 {os.path.relpath(file, PROJECT_ROOT)}")
    
    # Создаем директорию для логов
    logs_dir = os.path.join(PROJECT_ROOT, 'data', 'logs')
    os.makedirs(logs_dir, exist_ok=True)
    print(f"\n📁 Создана директория для логов: {logs_dir}")

if __name__ == "__main__":
    main()