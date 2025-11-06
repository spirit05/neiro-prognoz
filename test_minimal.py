# test_minimal.py
#!/usr/bin/env python3
"""
Минимальный тест системы
"""

import sys
import os

# Добавляем текущую директорию в путь
sys.path.insert(0, '/home/spirit/Desktop/project')

try:
    # Тест базовых импортов
    from config.paths import paths
    print(f"✅ paths: {paths.PROJECT_ROOT}")
    
    # Тест веб-интерфейса
    from web.app import main
    print("✅ Веб-интерфейс импортируется")
    
    print("🎉 СИСТЕМА РАБОТАЕТ!")
    
except Exception as e:
    print(f"❌ Ошибка: {e}")
    import traceback
    traceback.print_exc()
    