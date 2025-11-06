# fix_all_imports.py
#!/usr/bin/env python3
"""
Исправление всех импортов paths в проекте
"""

import os
import re

PROJECT_ROOT = '/home/spirit/Desktop/project'

def fix_imports_in_file(file_path):
    """Исправляет импорты paths в одном файле"""
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()

    original_content = content

    # Заменяем старые импорты на новые
    replacements = [
        # Заменяем прямой импорт DATASET, MODEL и т.д. на импорт paths
        (r'from config\.paths import (?:DATASET|MODEL|PREDICTIONS|LEARNING_RESULTS|TELEGRAM_CONFIG|SERVICE_STATE|INFO_JSON)', 
         'from config.paths import paths'),
        
        # Заменяем использование импортированных констант на paths.КОНСТАНТА
        (r'\bDATASET\b', 'paths.DATASET'),
        (r'\bMODEL\b', 'paths.MODEL'),
        (r'\bPREDICTIONS\b', 'paths.PREDICTIONS'),
        (r'\bLEARNING_RESULTS\b', 'paths.LEARNING_RESULTS'),
        (r'\bTELEGRAM_CONFIG\b', 'paths.TELEGRAM_CONFIG'),
        (r'\bSERVICE_STATE\b', 'paths.SERVICE_STATE'),
        (r'\bINFO_JSON\b', 'paths.INFO_JSON'),
    ]

    for pattern, replacement in replacements:
        content = re.sub(pattern, replacement, content)

    if content != original_content:
        print(f"✅ Исправлен: {file_path}")
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(content)
        return True

    return False

def main():
    """Основная функция"""
    print("🔧 Исправление импортов paths во всем проекте...")

    files_to_check = [
        'web/app.py',
        'ml/core/system.py',
        'ml/data/data_loader.py',
        'services/auto_learning/service.py',
        'services/telegram/notifier.py',
        'services/telegram/bot.py'
    ]

    fixed_files = []
    for file_path in files_to_check:
        full_path = os.path.join(PROJECT_ROOT, file_path)
        if os.path.exists(full_path):
            if fix_imports_in_file(full_path):
                fixed_files.append(file_path)

    print(f"\n📊 Исправлено файлов: {len(fixed_files)}")
    for file in fixed_files:
        print(f"   {file}")

if __name__ == "__main__":
    main()