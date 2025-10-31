# model/simple_nn/trainer.py
"""
Обучение УСИЛЕННОЙ нейросети
"""

import torch
import torch.nn as nn
import torch.optim as optim
import numpy as np
from typing import List
import os
from .model import EnhancedNumberPredictor
from .data_processor import DataProcessor

class EnhancedTrainer:
    def __init__(self, model_path: str = "data/simple_model.pth"):
        self.model_path = model_path
        self.device = torch.device('cpu')
        print(f"🔧 Используется устройство: {self.device}")
        self.model = None
        self.criterion = nn.CrossEntropyLoss()
        
    def train(self, groups: List[str], epochs: int = 25, batch_size: int = 128) -> None:  # Увеличили epochs и batch_size
        """Обучение модели с улучшенными параметрами"""
        processor = DataProcessor(history_size=25)  # Увеличили историю
        features, targets = processor.prepare_training_data(groups)
        
        if len(features) == 0:
            print(f"❌ Не удалось подготовить данные для обучения")
            return
        
        if len(features) < 100:
            print(f"❌ Недостаточно данных: {len(features)} примеров (нужно минимум 100)")
            return
        
        print(f"📊 Размер features: {features.shape}")
        print(f"📊 Размер targets: {targets.shape}")
        
        # Всегда создаем новую модель для чистого обучения
        self.model = EnhancedNumberPredictor(input_size=features.shape[1])
        self.model.to(self.device)
        
        # Улучшенный optimizer с learning rate scheduling
        self.optimizer = optim.AdamW(self.model.parameters(), lr=0.001, weight_decay=1e-4)
        self.scheduler = optim.lr_scheduler.ReduceLROnPlateau(self.optimizer, mode='min', factor=0.5, patience=3)
        
        # Используем CPU тензоры
        features_tensor = torch.tensor(features, dtype=torch.float32)
        targets_tensor = torch.tensor(targets, dtype=torch.long) - 1
        
        print(f"🧠 Начало обучения УСИЛЕННОЙ нейросети...")
        print(f"   • Эпохи: {epochs}")
        print(f"   • Batch size: {batch_size}")
        print(f"   • Примеров для обучения: {len(features)}")
        print(f"   • Learning rate: 0.001")
        print(f"   • Устройство: {self.device}")
        
        self.model.train()
        best_loss = float('inf')
        patience_counter = 0
        patience = 5  # Ранняя остановка
        
        for epoch in range(epochs):
            # Перемешиваем данные каждый эпох
            indices = torch.randperm(len(features))
            features_shuffled = features_tensor[indices]
            targets_shuffled = targets_tensor[indices]
            
            total_loss = 0
            num_batches = 0
            
            for i in range(0, len(features), batch_size):
                batch_end = min(i + batch_size, len(features))
                
                # Пропускаем слишком маленькие батчи
                if batch_end - i < 2:
                    continue
                    
                batch_features = features_shuffled[i:batch_end]
                batch_targets = targets_shuffled[i:batch_end]
                
                self.optimizer.zero_grad()
                outputs = self.model(batch_features)
                
                # Вычисляем loss с весами для каждой позиции
                loss = 0
                for j in range(4):
                    loss += self.criterion(outputs[:, j, :], batch_targets[:, j])
                loss = loss / 4
                
                # L2 regularization
                l2_lambda = 0.001
                l2_norm = sum(p.pow(2.0).sum() for p in self.model.parameters())
                loss = loss + l2_lambda * l2_norm
                
                loss.backward()
                
                # Gradient clipping
                torch.nn.utils.clip_grad_norm_(self.model.parameters(), max_norm=1.0)
                self.optimizer.step()
                
                total_loss += loss.item()
                num_batches += 1
            
            if num_batches > 0:
                avg_loss = total_loss / num_batches
                current_lr = self.optimizer.param_groups[0]['lr']
                
                print(f"📈 Эпоха {epoch+1}/{epochs}, Loss: {avg_loss:.4f}, LR: {current_lr:.6f}")
                
                # Learning rate scheduling
                self.scheduler.step(avg_loss)
                
                if avg_loss < best_loss:
                    best_loss = avg_loss
                    self._save_model()
                    patience_counter = 0
                    print(f"💾 Сохранена лучшая модель (loss: {avg_loss:.4f})")
                else:
                    patience_counter += 1
                    if patience_counter >= patience:
                        print(f"🛑 Ранняя остановка на эпохе {epoch+1}")
                        break
            else:
                print(f"⚠️  Эпоха {epoch+1}/{epochs}: нет валидных батчей")
        
        print(f"✅ Обучение завершено! Лучший loss: {best_loss:.4f}")
        
        # Анализируем качество модели
        self._analyze_model_performance(features_tensor, targets_tensor)
    
    def _analyze_model_performance(self, features_tensor: torch.Tensor, targets_tensor: torch.Tensor):
        """Анализ производительности модели"""
        self.model.eval()
        with torch.no_grad():
            # Берем небольшой subset для анализа
            test_size = min(1000, len(features_tensor))
            test_features = features_tensor[:test_size]
            test_targets = targets_tensor[:test_size] + 1  # Возвращаем к 1-26
            
            outputs = self.model(test_features)
            predictions = torch.argmax(outputs, dim=-1) + 1  # [batch_size, 4]
            
            # Вычисляем accuracy
            correct = (predictions == test_targets).float()
            accuracy = correct.mean().item()
            
            print(f"📊 Accuracy на тестовых данных: {accuracy:.4f}")
            
            # Анализируем распределение предсказаний
            unique_predictions = len(torch.unique(predictions))
            print(f"📊 Уникальных предсказанных чисел: {unique_predictions}/26")
    
    def _save_model(self):
        """Сохранение модели"""
        if self.model is not None:
            os.makedirs(os.path.dirname(self.model_path), exist_ok=True)
            torch.save({
                'model_state_dict': self.model.state_dict(),
                'model_config': {
                    'input_size': self.model.feature_extractor[0].in_features,
                    'hidden_size': self.model.feature_extractor[0].out_features
                }
            }, self.model_path)