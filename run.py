# [file name]: run.py (ОБНОВЛЕННЫЙ)
# run.py
"""
Главный запускающий файл для УСИЛЕННОЙ нейросети с ансамблевыми методами
"""

import os
import sys

# Добавляем текущую директорию в путь для импортов
sys.path.insert(0, os.path.dirname(__file__))

from model.cli import main_menu

if __name__ == "__main__":
    # Создаем необходимые директории
    os.makedirs('data', exist_ok=True)
    
    print("🚀 Запуск УСИЛЕННОЙ нейросети для предсказания чисел...")
    print("   Теперь с ансамблевыми методами и улучшенной точностью! 🎯")
    main_menu()