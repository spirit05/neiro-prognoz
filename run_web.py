#!/usr/bin/env python3
"""
Обертка для запуска Streamlit с правильными путями
"""

import sys
import os

# Принудительно устанавливаем пути
PROJECT_PATH = '/opt/project'
sys.path.insert(0, PROJECT_PATH)
sys.path.insert(0, os.path.join(PROJECT_PATH, 'model'))

print(f"🔧 PYTHONPATH: {sys.path}")

# Проверяем импорты
try:
    from model.simple_system import SimpleNeuralSystem
    from model.data_loader import load_dataset
    print("✅ Все импорты успешны!")
    
    # Тестируем систему
    system = SimpleNeuralSystem()
    print("✅ Система инициализирована!")
    
except Exception as e:
    print(f"❌ Ошибка импорта: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

# Запускаем Streamlit
if __name__ == "__main__":
    # Импортируем и запускаем app.py через Streamlit
    from streamlit.web.cli import main
    sys.argv = ["streamlit", "run", "app.py", "--server.port=8501", "--server.address=0.0.0.0"]
    sys.exit(main())
