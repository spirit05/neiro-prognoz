# [file name]: run.py (УПРОЩЕННЫЙ)
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
log_dir = "/var/log"
log_file = os.path.join(log_dir, "sequence-predictor.log")

try:
    # Пытаемся писать в /var/log, если нет прав - пишем в текущую директорию
    if not os.access(log_dir, os.W_OK):
        log_file = "sequence-predictor.log"
        print(f"⚠️  Нет прав на запись в {log_dir}, логи в: {log_file}")
except:
    log_file = "sequence-predictor.log"

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout),
        logging.FileHandler(log_file)
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
        data_dir = os.path.join(current_dir, 'data')
        os.makedirs(data_dir, exist_ok=True)
        logger.info(f"✅ Директории проверены: {data_dir}")
        
        # Импортируем систему напрямую (избегаем циклических импортов)
        sys.path.insert(0, os.path.join(current_dir, 'model'))
        from simple_system import SimpleNeuralSystem
        from cli import main_menu
        
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
        logger.error(f"❌ Критическая ошибка при запуске: {e}", exc_info=True)
        sys.exit(1)

if __name__ == "__main__":
    main()