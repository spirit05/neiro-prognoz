# /opt/dev/web/run_web.py
#!/usr/bin/env python3
"""
Запуск веб-интерфейса для новой архитектуры - ПОЛНАЯ ИНТЕГРАЦИЯ
"""

import sys
import os

# ⚡ ПРИНУДИТЕЛЬНО УСТАНАВЛИВАЕМ ПУТИ ДЛЯ НОВОЙ АРХИТЕКТУРЫ
PROJECT_PATH = '/opt/dev'
sys.path.insert(0, PROJECT_PATH)

print(f"🚀 Запуск ПОЛНОГО веб-интерфейса в DEV среде...")
print(f"📁 Рабочая директория: {PROJECT_PATH}")

# 🔧 ПРОВЕРЯЕМ ВСЕ НЕОБХОДИМЫЕ ИМПОРТЫ
try:
    print("🔍 Проверка импортов новой архитектуры...")
    
    # Конфигурация
    from config import paths
    from config.constants import *
    print("✅ Конфигурация")
    
    # ML система
    from ml.learning.self_learning import SelfLearningSystem
    from ml.core.predictor import EnhancedPredictor
    from ml.core.data_processor import DataProcessor
    print("✅ ML компоненты")
    
    # Сервисы
    from services.auto_learning.service import AutoLearningService
    print("✅ Сервисы")
    
    # Утилиты данных
    from ml.utils.data_utils import load_dataset, save_dataset, save_predictions, load_predictions
    print("✅ Утилиты данных")
    
    print("🎯 ВСЕ ИМПОРТЫ УСПЕШНЫ! Система готова к работе.")
    
    # Тестовая инициализация
    print("🔧 Тестовая инициализация компонентов...")
    system = SelfLearningSystem()
    predictor = EnhancedPredictor()
    predictor.load_model()
    
    print(f"✅ SelfLearningSystem: {system.get_performance_stats()}")
    print(f"✅ EnhancedPredictor: Модель загружена - {predictor.is_trained}")
    
    # Проверка данных
    dataset = load_dataset()
    print(f"✅ Данные: {len(dataset)} групп в датасете")
    
except Exception as e:
    print(f"❌ Ошибка импорта: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

# 🚀 ЗАПУСКАЕМ STREAMLIT
if __name__ == "__main__":
    from streamlit.web.cli import main
    
    # 🔧 ЗАПУСК НА ПОРТУ 8502 ДЛЯ DEV СРЕДЫ
    sys.argv = [
        "streamlit", "run", 
        "web/app.py", 
        "--server.port=8502",           # 🔧 DEV порт
        "--server.address=0.0.0.0",
        "--theme.base=light",
        "--browser.gatherUsageStats=false"
    ]
    
    print(f"🌐 Запуск Streamlit на порту 8502...")
    print(f"📊 PROD система работает на порту 8501")
    print(f"🔧 DEV система запускается на порту 8502")
    print(f"🎯 Доступно по адресу: http://0.0.0.0:8502")
    
    sys.exit(main())