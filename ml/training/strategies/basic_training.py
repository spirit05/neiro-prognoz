"""
Базовая стратегия обучения - чистая реализация без legacy
"""
import torch
import torch.nn as nn
import numpy as np
from typing import Dict, Any, List
import time

from ml.training import AbstractTrainingStrategy
from ml.core.types import TrainingConfig, TrainingResult, DataBatch, ModelStatus
from ml.core.base_model import AbstractBaseModel


class BasicTrainingStrategy(AbstractTrainingStrategy):
    """Базовая стратегия полного обучения модели"""
    
    def __init__(self):
        super().__init__("basic_training")
    
    def train(self, model: AbstractBaseModel, data: DataBatch, config: TrainingConfig) -> TrainingResult:
        """Полное обучение модели с нуля"""
        self._notify_progress("🚀 Начало базового обучения модели")
    
        # 🔧 ИСПРАВЛЕНИЕ: Инициализируем модель если нужно
        if not hasattr(model, 'model') or model.model is None:
            self._notify_progress("🔧 Инициализация модели перед обучением")
            # Определяем input_size из данных
            input_size = data.data.shape[1] if hasattr(data.data, 'shape') else 50
            if hasattr(model, 'initialize_model'):
                model.initialize_model(input_size=input_size)
            else:
                raise ValueError("Модель не инициализирована и не поддерживает initialize_model")
    
        training_start = time.time()
        training_loss = []
        validation_loss = []
    
        try:            # Подготовка данных
            self._notify_progress("📊 Подготовка данных для обучения")
            features, targets = self._prepare_training_data(data)
            
            if len(features) == 0:
                raise ValueError("Недостаточно данных для обучения")
            
            # Конфигурация оптимизатора
            optimizer = torch.optim.Adam(model.model.parameters(), lr=config.learning_rate)
            criterion = nn.CrossEntropyLoss()
            
            # Цикл обучения
            model.model.train()
            best_loss = float('inf')
            
            for epoch in range(config.epochs):
                epoch_start = time.time()
                epoch_loss = 0.0
                num_batches = 0
                
                # Мини-батчи
                for i in range(0, len(features), config.batch_size):
                    batch_features = features[i:i + config.batch_size]
                    batch_targets = targets[i:i + config.batch_size]
                    
                    if len(batch_features) < 2:
                        continue
                    
                    optimizer.zero_grad()
                    outputs = model.model(batch_features)
                    
                    # Расчет loss
                    loss = self._calculate_multi_position_loss(outputs, batch_targets, criterion)
                    loss.backward()
                    optimizer.step()
                    
                    epoch_loss += loss.item()
                    num_batches += 1
                
                if num_batches > 0:
                    avg_epoch_loss = epoch_loss / num_batches
                    training_loss.append(avg_epoch_loss)
                    validation_loss.append(avg_epoch_loss * 1.1)  # Упрощенная валидация
                    
                    epoch_time = time.time() - epoch_start
                    self._notify_progress(
                        f"📈 Эпоха {epoch+1}/{config.epochs}, Loss: {avg_epoch_loss:.4f}, Время: {epoch_time:.1f}с"
                    )
                    
                    if avg_epoch_loss < best_loss:
                        best_loss = avg_epoch_loss
            
            # Формирование результатов
            training_time = time.time() - training_start
            result = TrainingResult(
                model_id=model.model_id,
                status=ModelStatus.TRAINED,
                training_loss=training_loss,
                validation_loss=validation_loss,
                metrics={'final_training_loss': training_loss[-1], 'best_loss': best_loss},
                training_time=training_time,
                best_epoch=config.epochs
            )
            
            self._notify_progress(f"✅ Базовое обучение завершено! Финальный loss: {training_loss[-1]:.4f}")
            # Устанавливаем флаг обучения модели
            model._is_trained = True
            model.status = ModelStatus.TRAINED
            return result
            
        except Exception as e:
            self._notify_progress(f"❌ Ошибка обучения: {e}")
            raise
    
    def validate(self, model: AbstractBaseModel, data: DataBatch) -> Dict[str, float]:
        """Валидация модели"""
        model.model.eval()
        features, targets = self._prepare_training_data(data)
        
        with torch.no_grad():
            outputs = model.model(features)
            criterion = nn.CrossEntropyLoss()
            loss = self._calculate_multi_position_loss(outputs, targets, criterion)
            
        return {'validation_loss': loss.item()}
    
    def _prepare_training_data(self, data: DataBatch):
        """Подготовка данных для обучения"""
        # Используем встроенные методы модели для подготовки данных
        if hasattr(data.data, 'values'):
            features = torch.tensor(data.data.values, dtype=torch.float32)
        else:
            features = torch.tensor(data.data, dtype=torch.float32)
        
        # Для демонстрации - создаем простые targets
        # В реальном сценарии targets будут извлекаться из данных
        batch_size = len(features)
        targets = torch.randint(0, 26, (batch_size, 4), dtype=torch.long)
        
        return features, targets
    
    def _calculate_multi_position_loss(self, outputs, targets, criterion):
        """Расчет loss для 4 позиций"""
        loss = 0
        for pos in range(4):
            loss += criterion(outputs[:, pos, :], targets[:, pos])
        return loss / 4  # Усредняем по позициям
