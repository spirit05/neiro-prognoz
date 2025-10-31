# retrain_model.py
"""
Скрипт для полного переобучения модели
"""

import os
import sys
sys.path.insert(0, os.path.dirname(__file__))

from model.simple_nn.trainer import SimpleTrainer
from model.data_loader import load_dataset

def retrain_model():
    """Полное переобучение модели"""
    print("🔄 Полное переобучение модели...")
    
    groups = load_dataset()
    if not groups:
        print("❌ Нет данных для обучения")
        return
    
    print(f"📊 Загружено {len(groups)} групп")
    
    # Удаляем старую модель для чистого переобучения
    model_path = "data/simple_model.pth"
    if os.path.exists(model_path):
        os.remove(model_path)
        print("🗑️  Удалена старая модель")
    
    # Обучаем с нуля
    trainer = SimpleTrainer(model_path)
    trainer.train(groups, epochs=15, batch_size=64)
    
    print("✅ Переобучение завершено!")

if __name__ == "__main__":
    retrain_model()