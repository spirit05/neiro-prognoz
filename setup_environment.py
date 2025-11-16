# /opt/model/setup_environment.py
"""
Скрипт для настройки окружения и проверки импортов
"""
import sys
import os

def setup_environment():
    """Настройка окружения для корректной работы импортов"""
    
    # Получаем абсолютный путь к корневой директории проекта
    current_dir = os.path.dirname(os.path.abspath(__file__))
    
    # Добавляем в Python path
    if current_dir not in sys.path:
        sys.path.insert(0, current_dir)
        print(f"✅ Добавлен путь: {current_dir}")
    
    # Проверяем существование ключевых директорий
    required_dirs = ['ml', 'ml/core', 'ml/learning', 'tests']
    for dir_name in required_dirs:
        dir_path = os.path.join(current_dir, dir_name)
        if os.path.exists(dir_path):
            print(f"✅ Директория найдена: {dir_path}")
        else:
            print(f"❌ Директория не найдена: {dir_path}")
            return False
    
    return True

def test_imports():
    """Тестирование всех ключевых импортов"""
    imports_to_test = [
        ('ml.core.types', ['DataBatch', 'DataType', 'AnalysisResult']),
        ('ml.core.base_model', ['AbstractBaseModel']),
        ('ml.core.orchestrator', ['MLOrchestrator']),
        ('ml.ensemble.base_ensemble', ['AbstractEnsemblePredictor']),
    ]
    
    all_success = True
    
    for module_name, classes in imports_to_test:
        try:
            module = __import__(module_name, fromlist=classes)
            for class_name in classes:
                if hasattr(module, class_name):
                    print(f"✅ {module_name}.{class_name} - OK")
                else:
                    print(f"❌ {module_name}.{class_name} - не найден")
                    all_success = False
        except ImportError as e:
            print(f"❌ Ошибка импорта {module_name}: {e}")
            all_success = False
    
    return all_success

if __name__ == "__main__":
    print("🔧 Настройка окружения...")
    
    if setup_environment():
        print("\n🧪 Тестирование импортов...")
        if test_imports():
            print("\n🎉 Все импорты работают корректно!")
        else:
            print("\n🔧 Требуется дополнительная настройка")
    else:
        print("\n❌ Настройка окружения не удалась")
