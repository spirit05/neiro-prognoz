# [file name]: run.py (ОБНОВЛЕННЫЙ ДЛЯ SYSTEMD)
#!/usr/bin/env python3
"""
Главный запускающий файл для УСИЛЕННОЙ нейросети с ансамблевыми методами
Запускается через systemd сервис
"""

import os
import sys
import time
import logging
from datetime import datetime

# Настройка логирования для systemd
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout),
        logging.FileHandler('/var/log/sequence-predictor.log')
    ]
)
logger = logging.getLogger('SequencePredictor')

# Добавляем текущую директорию в путь для импортов
current_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, current_dir)

def main():
    try:
        logger.info("🚀 Запуск УСИЛЕННОЙ нейросети для предсказания чисел...")
        logger.info("   Теперь с ансамблевыми методами, самообучением и улучшенной точностью! 🎯")
        
        # Создаем необходимые директории
        os.makedirs('data', exist_ok=True)
        logger.info("✅ Директории проверены")
        
        # Импортируем и запускаем систему
        from model.simple_system import SimpleNeuralSystem
        from model.cli import main_menu
        
        # Инициализируем систему
        system = SimpleNeuralSystem()
        logger.info("✅ Система инициализирована")
        
        # Запускаем CLI интерфейс
        logger.info("✅ Запуск основного меню")
        main_menu()
        
    except KeyboardInterrupt:
        logger.info("⏹️  Остановка системы по запросу пользователя")
        sys.exit(0)
    except Exception as e:
        logger.error(f"❌ Критическая ошибка при запуске: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()