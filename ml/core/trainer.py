# ml/core/trainer.py - ИСПРАВЛЯЕМ ЛОГИРОВАНИЕ

import os
import sys
import time
import json
from datetime import datetime

# Добавляем пути для импорта
PROJECT_ROOT = '/home/spirit/Desktop/project'
sys.path.insert(0, PROJECT_ROOT)
sys.path.insert(0, os.path.join(PROJECT_ROOT, 'ml'))

from utils.logging_system import get_training_logger

# Инициализируем логгер
logger = get_training_logger()

class EnhancedTrainer:
    def __init__(self, model_path):
        self.model_path = model_path
        self.start_time = None
        self.epoch_start_time = None
        
    def train(self, groups, epochs=20, batch_size=64):
        """Обучение модели с улучшенным логированием"""
        self.start_time = time.time()
        
        try:
            logger.info(f"🚀 Начало обучения модели на {len(groups)} группах...")
            logger.info(f"📊 Параметры: {epochs} эпох, batch_size={batch_size}")
            
            # Здесь должна быть реальная логика обучения
            # Пока эмулируем обучение для тестирования
            for epoch in range(epochs):
                self.epoch_start_time = time.time()
                
                # Эмуляция процесса обучения
                time.sleep(0.1)  # Имитация вычислений
                
                # Логируем прогресс
                if (epoch + 1) % 5 == 0 or epoch == 0 or epoch == epochs - 1:
                    elapsed = time.time() - self.epoch_start_time
                    logger.info(f"📈 Эпоха {epoch + 1}/{epochs} завершена за {elapsed:.2f} сек")
            
            total_time = time.time() - self.start_time
            logger.info(f"✅ Обучение завершено за {total_time:.2f} секунд")
            
            # Сохраняем модель
            self._save_model()
            
            return True
            
        except Exception as e:
            logger.error(f"❌ Ошибка обучения: {e}")
            return False
    
    def _save_model(self):
        """Сохранение модели с логированием"""
        try:
            # Создаем директорию если не существует
            os.makedirs(os.path.dirname(self.model_path), exist_ok=True)
            
            # Здесь должна быть реальная логика сохранения модели
            # Пока создаем заглушку
            with open(self.model_path, 'w') as f:
                f.write(f"# Модель обучена {datetime.now().isoformat()}\n")
            
            logger.info(f"💾 Модель сохранена: {self.model_path}")
            
        except Exception as e:
            logger.error(f"❌ Ошибка сохранения модели: {e}")
            raise
    
    def continue_training(self, groups, additional_epochs=5):
        """Продолжение обучения с логированием"""
        logger.info(f"🔄 Продолжение обучения на {len(groups)} группах...")
        logger.info(f"📊 Дополнительные эпохи: {additional_epochs}")
        
        return self.train(groups, epochs=additional_epochs)