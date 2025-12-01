"""
Скрипт для создания необходимых директорий для Telegram бота
"""

import os
from pathlib import Path

def setup_directories():
    """Создание необходимых директорий"""
    project_root = Path(__file__).parent
    
    directories = [
        project_root / 'config',
        project_root / 'data' / 'logs',
        project_root / 'data' / 'models',
        project_root / 'data' / 'datasets',
        project_root / 'data' / 'analytics',
        project_root / 'data' / 'debug',
    ]
    
    print("🔧 Создание структуры директорий...")
    
    for directory in directories:
        directory.mkdir(parents=True, exist_ok=True)
        print(f"  ✅ Создана: {directory.relative_to(project_root)}")
    
    # Создаем пустые файлы если их нет
    files_to_create = [
        (project_root / 'config' / 'telegram_config.yaml', 
         '# Конфигурация Telegram бота\n# Заполните bot_token и chat_id\n'),
        (project_root / 'data' / 'logs' / 'telegram_bot.log', ''),
    ]
    
    for file_path, content in files_to_create:
        if not file_path.exists():
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(content)
            print(f"  ✅ Создан файл: {file_path.relative_to(project_root)}")
    
    print("\n✅ Структура директорий создана!")
    print(f"📁 Логи будут сохраняться в: data/logs/")
    print(f"⚙️ Конфигурация: config/telegram_config.yaml")

if __name__ == "__main__":
    setup_directories()
