# /opt/model/tests/test_basic_imports.py
"""
Базовый тест для проверки импортов
"""
import sys
import os

def test_python_path():
    """Проверка корректности Python path"""
    current_dir = os.path.dirname(os.path.abspath(__file__))
    parent_dir = os.path.dirname(current_dir)
    
    print(f"Current dir: {current_dir}")
    print(f"Parent dir: {parent_dir}")
    print(f"Python path: {sys.path}")
    
    # Проверяем что корневая директория в пути
    assert parent_dir in sys.path, f"Parent directory {parent_dir} not in Python path"
    print("✅ Python path настроен корректно")

def test_ml_import():
    """Проверка импорта ML модулей"""
    try:
        # Пробуем импортировать базовые модули
        from ml.core.types import DataBatch, DataType
        from ml.core.base_model import AbstractBaseModel
        
        print("✅ Базовые импорты работают")
        assert True
    except ImportError as e:
        print(f"❌ Ошибка импорта: {e}")
        assert False

if __name__ == "__main__":
    test_python_path()
    success = test_ml_import()
    if success:
        print("🎉 Все базовые импорты работают!")
    else:
        print("🔧 Требуется настройка путей")
