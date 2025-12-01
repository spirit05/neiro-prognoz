# tests/quick_cleanup_test.py
import os
import sys

# 🔧 ДОБАВЛЯЕМ корневую директорию в sys.path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

def test_essential_files():
    """Проверка наличия основных файлов"""
    essential_files = [
        "data/models/enhanced_predictor_v2.pth",
        "data/datasets/dataset.json", 
        "web/app.py",
        "ml/core/orchestrator.py",
        "ml/models/base/enhanced_predictor.py"
    ]
    
    missing_files = []
    for file_path in essential_files:
        if not os.path.exists(file_path):
            missing_files.append(file_path)
    
    if missing_files:
        print("❌ Отсутствуют файлы:", missing_files)
        return False
    else:
        print("✅ Все основные файлы на месте")
        return True

def test_imports():
    """Проверка основных импортов"""
    try:
        from ml.core.orchestrator import MLOrchestrator
        from ml.models.base import EnhancedPredictor
        from ml.data.providers import DatasetManager, PredictionsManager
        print("✅ Основные импорты работают")
        return True
    except ImportError as e:
        print(f"❌ Ошибка импорта: {e}")
        return False

def test_no_data_utils_imports():
    """Проверка что нет импортов из data_utils"""
    import subprocess
    # 🔧 ИСПРАВЛЕНИЕ: Исключаем сам тестовый файл из поиска
    result = subprocess.run(
        ["grep", "-r", "from ml.utils.data_utils", "/opt/model/", 
         "--include=*.py", "--exclude=quick_cleanup_test.py"],
        capture_output=True, text=True
    )
    
    if result.stdout:
        print("❌ Найдены оставшиеся импорты из data_utils:")
        print(result.stdout)
        return False
    else:
        print("✅ Нет импортов из data_utils")
        return True

if __name__ == "__main__":
    print("🧹 Финальная проверка после очистки проекта...")
    
    files_ok = test_essential_files()
    imports_ok = test_imports()
    no_data_utils = test_no_data_utils_imports()
    
    if files_ok and imports_ok and no_data_utils:
        print("🎉 Проект успешно очищен и готов к работе!")
    else:
        print("⚠️ Требуется дополнительная настройка")
