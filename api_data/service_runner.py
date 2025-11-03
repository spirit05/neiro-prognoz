# api_data/service_runner.py
#!/usr/bin/env python3
"""
Запуск сервиса автообучения как демона
"""

import os
import sys
import time
import logging
from datetime import datetime

# Добавляем пути
PROJECT_PATH = '/opt/project'
sys.path.insert(0, PROJECT_PATH)
sys.path.insert(0, os.path.dirname(__file__))

from auto_learning_service import AutoLearningService

# Настройка логирования
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('/opt/project/api_data/service_runner.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger('ServiceRunner')

def main():
    """Основная функция запуска сервиса"""
    logger.info("🎯 Запуск сервиса автообучения...")
    
    max_retries = 3
    retry_delay = 60  # секунды
    
    for attempt in range(max_retries):
        try:
            service = AutoLearningService()
            if service.system:
                logger.info("✅ Сервис успешно инициализирован")
                service.start_scheduled_service()
                break
            else:
                logger.error(f"❌ Попытка {attempt + 1}/{max_retries}: Не удалось инициализировать сервис")
        except Exception as e:
            logger.error(f"❌ Попытка {attempt + 1}/{max_retries}: Ошибка запуска сервиса: {e}")
            
            if attempt < max_retries - 1:
                logger.info(f"⏳ Повторная попытка через {retry_delay} секунд...")
                time.sleep(retry_delay)
            else:
                logger.error("🛑 Достигнуто максимальное количество попыток. Сервис остановлен.")
                sys.exit(1)

if __name__ == "__main__":
    main()