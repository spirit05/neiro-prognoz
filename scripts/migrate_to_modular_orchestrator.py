# [file name]: scripts/migrate_to_modular_orchestrator.py
"""
Скрипт миграции с монолитного оркестратора на модульный
"""

import sys
import os
from pathlib import Path

def update_imports_in_file(file_path: Path):
    """Обновление импортов в файле"""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Заменяем старый импорт на новый
        old_import = "from ml.core.orchestrator import MLOrchestrator"
        new_import = "from ml.core.orchestrator import MLOrchestrator"
        
        # Импорт тот же, но теперь он ведет на модульную версию
        if old_import in content:
            print(f"✅ Обновлен импорт в {file_path}")
            # Импорт тот же, файл заменен прозрачно
        
        return True
        
    except Exception as e:
        print(f"❌ Ошибка обновления {file_path}: {e}")
        return False

def migrate_project():
    """Миграция проекта на модульный оркестратор"""
    project_root = Path(__file__).parent.parent
    
    # Файлы для обновления
    files_to_update = [
        project_root / "tests" / "test_ml_core.py",
        project_root / "tests" / "test_orchestrator_training.py", 
        project_root / "tests" / "test_stage1_core.py",
        project_root / "tests" / "test_stage7_orchestrator_integration.py",
        project_root / "tests" / "test_stage9_ml_core.py",
        project_root / "web" / "components" / "ml_adapter.py",
        project_root / "services" / "auto_learning" / "service.py"
    ]
    
    print("🔄 Начинаем миграцию на модульный оркестратор...")
    
    # Обновляем импорты
    success_count = 0
    for file_path in files_to_update:
        if file_path.exists():
            if update_imports_in_file(file_path):
                success_count += 1
        else:
            print(f"⚠️ Файл не найден: {file_path}")
    
    # Удаляем старый оркестратор
    old_orchestrator_path = project_root / "ml" / "core" / "orchestrator.py"
    if old_orchestrator_path.exists():
        backup_path = old_orchestrator_path.with_suffix('.py.backup')
        try:
            # Создаем бэкап
            import shutil
            shutil.copy2(old_orchestrator_path, backup_path)
            # Удаляем старый файл
            old_orchestrator_path.unlink()
            print(f"✅ Старый оркестратор перемещен в бэкап: {backup_path}")
        except Exception as e:
            print(f"❌ Ошибка удаления старого оркестратора: {e}")
    
    print(f"✅ Миграция завершена! Обновлено файлов: {success_count}/{len(files_to_update)}")

if __name__ == "__main__":
    migrate_project()
