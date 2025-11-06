from config.paths import paths
# [file name]: model/simple_nn/trainer.py (ИСПРАВЛЕННЫЙ)
"""
Обучение УСИЛЕННОЙ нейросети - ИСПРАВЛЕННЫЙ
"""

import torch
import torch.nn as nn
import torch.optim as optim
import numpy as np
from typing import List, Tuple
import os
import time
import gc
from .model import EnhancedNumberPredictor
from .data_processor import DataProcessor

class EnhancedTrainer:
    def __init__(self, model_path: str = "data/simple_model.pth"):
        self.model_path = model_path
        self.device = torch.device('cpu')
        self.model = None
        self.criterion = nn.CrossEntropyLoss()
        self.progress_callback = None
    
    def set_progress_callback(self, callback):
        """Установка callback для прогресса"""
        self.progress_callback = callback
    
    def _report_progress(self, message):
        """Отправка сообщения о прогрессе с записью в файл"""
        import datetime
        timestamp = datetime.datetime.now().strftime('%H:%M:%S')
        formatted_message = f"{timestamp} - {message}"
        
        # Записываем в файл
        try:
            with open(paths.TRAINING_LOG, "a", encoding="utf-8") as f:
                f.write(formatted_message + "\n")
        except Exception as e:
            print(f"❌ Ошибка записи в лог: {e}")
        
        # Старая логика
        if self.progress_callback:
            self.progress_callback(message)
        else:
            print(f"📢 {message}")
    
    def train(self, groups: List[str], epochs: int = 20, batch_size: int = 64) -> List[Tuple[Tuple[int, int, int, int], float]]:
        """Обучение модели с улучшенными параметрами и детальным логированием"""
        total_start_time = time.time()
        
        self._report_progress(f"🚀 СТАРТ обучения: {len(groups)} групп, {epochs} эпох, batch_size={batch_size}")
        
        # Этап 1: Подготовка данных
        stage1_start = time.time()
        self._report_progress("📊 Этап 1: Подготовка данных...")
        
        processor = DataProcessor(history_size=25)
        features, targets = processor.prepare_training_data(groups)
        
        stage1_time = time.time() - stage1_start
        self._report_progress(f"✅ Этап 1 завершен: {stage1_time:.1f} сек")
        
        if len(features) == 0:
            self._report_progress("❌ Не удалось подготовить данные для обучения")
            return []
        
        if len(features) < 100:
            self._report_progress(f"❌ Недостаточно данных: {len(features)} примеров (нужно минимум 100)")
            return []
        
        self._report_progress(f"✅ Обработано {len(groups)} групп, {len(groups)*4} чисел")
        self._report_progress(f"✅ Создано {len(features)} обучающих примеров")
        
        # Этап 2: Создание модели
        stage2_start = time.time()
        self._report_progress("🔧 Этап 2: Создание модели...")
        
        # Всегда создаем новую модель для чистого обучения
        self.model = EnhancedNumberPredictor(input_size=features.shape[1], hidden_size=256)
        self.model.to(self.device)
        
        # Оптимизация памяти для 4 ГБ RAM
        torch.backends.cudnn.deterministic = True
        torch.backends.cudnn.benchmark = False
        
        stage2_time = time.time() - stage2_start
        self._report_progress(f"✅ Этап 2 завершен: {stage2_time:.1f} сек")
        
        # Этап 3: Настройка оптимизатора
        stage3_start = time.time()
        self._report_progress("⚙️ Этап 3: Настройка оптимизатора...")
        
        # Улучшенный optimizer с learning rate scheduling
        self.optimizer = optim.AdamW(self.model.parameters(), lr=0.001, weight_decay=1e-4)
        self.scheduler = optim.lr_scheduler.ReduceLROnPlateau(self.optimizer, mode='min', factor=0.5, patience=3)
        
        stage3_time = time.time() - stage3_start
        self._report_progress(f"✅ Этап 3 завершен: {stage3_time:.1f} сек")
        
        # Используем CPU тензоры
        features_tensor = torch.tensor(features, dtype=torch.float32)
        targets_tensor = torch.tensor(targets, dtype=torch.long) - 1
        
        # Этап 4: Обучение модели
        stage4_start = time.time()
        self._report_progress("🧠 Этап 4: Обучение модели...")
        
        self.model.train()
        best_loss = float('inf')
        patience_counter = 0
        patience = 5
        
        for epoch in range(epochs):
            epoch_start_time = time.time()
            
            # Перемешиваем данные каждый эпох
            indices = torch.randperm(len(features))
            features_shuffled = features_tensor[indices]
            targets_shuffled = targets_tensor[indices]
            
            total_loss = 0
            num_batches = 0
            
            for i in range(0, len(features), batch_size):
                batch_start = i
                batch_end = min(i + batch_size, len(features))
                
                if batch_end - batch_start < 2:
                    continue
                    
                batch_features = features_shuffled[batch_start:batch_end]
                batch_targets = targets_shuffled[batch_start:batch_end]
                
                self.optimizer.zero_grad()
                outputs = self.model(batch_features)
                
                loss = 0
                for j in range(4):
                    loss += self.criterion(outputs[:, j, :], batch_targets[:, j])
                loss = loss / 4
                
                # L2 регуляризация
                l2_lambda = 0.001
                l2_norm = sum(p.pow(2.0).sum() for p in self.model.parameters())
                loss = loss + l2_lambda * l2_norm
                
                loss.backward()
                torch.nn.utils.clip_grad_norm_(self.model.parameters(), max_norm=1.0)
                self.optimizer.step()
                
                total_loss += loss.item()
                num_batches += 1
            
            epoch_time = time.time() - epoch_start_time
            
            if num_batches > 0:
                avg_loss = total_loss / num_batches
                current_lr = self.optimizer.param_groups[0]['lr']
                
                self._report_progress(f"📈 Эпоха {epoch+1}/{epochs}, Loss: {avg_loss:.4f}, LR: {current_lr:.6f}, Время: {epoch_time:.1f} сек")
                
                self.scheduler.step(avg_loss)
                
                if avg_loss < best_loss:
                    best_loss = avg_loss
                    self._save_model()
                    patience_counter = 0
                    self._report_progress(f"💾 Сохранена лучшая модель (loss: {avg_loss:.4f})")
                else:
                    patience_counter += 1
                    if patience_counter >= patience:
                        self._report_progress(f"🛑 Ранняя остановка на эпохе {epoch+1}")
                        break
            else:
                self._report_progress(f"⚠️  Эпоха {epoch+1}/{epochs}: нет валидных батчей")
        
        stage4_time = time.time() - stage4_start
        self._report_progress(f"✅ Этап 4 завершен: {stage4_time:.1f} сек")
        self._report_progress(f"✅ Обучение завершено! Лучший loss: {best_loss:.4f}")
        
        # Этап 5: Анализ производительности
        stage5_start = time.time()
        self._report_progress("📊 Этап 5: Анализ производительности...")
        
        self._analyze_model_performance(features_tensor, targets_tensor)
        
        stage5_time = time.time() - stage5_start
        self._report_progress(f"✅ Этап 5 завершен: {stage5_time:.1f} сек")
        
        # Этап 6: Очистка памяти
        stage6_start = time.time()
        self._report_progress("🧹 Этап 6: Очистка памяти...")
        
        # Очистка памяти
        del features_tensor, targets_tensor, features_shuffled, targets_shuffled
        gc.collect()
        if torch.cuda.is_available():
            torch.cuda.empty_cache()
        
        stage6_time = time.time() - stage6_start
        self._report_progress(f"✅ Этап 6 завершен: {stage6_time:.1f} сек")
        
        total_time = time.time() - total_start_time
        self._report_progress(f"🎉 ВСЕ ЭТАПЫ ЗАВЕРШЕНЫ! Общее время: {total_time:.1f} сек")
        
        # Генерация прогнозов после обучения
        self._report_progress("🔮 Генерация прогнозов после обучения...")
        
        # Создаем временный predictor для генерации прогнозов
        from .predictor import EnhancedPredictor
        predictor = EnhancedPredictor(self.model_path)
        if predictor.load_model():
            # Генерируем прогнозы на основе обучающих данных
            recent_numbers = []
            for group_str in groups[-25:]:
                try:
                    numbers = [int(x) for x in group_str.strip().split()]
                    if len(numbers) == 4:
                        recent_numbers.extend(numbers)
                except:
                    continue
            
            if len(recent_numbers) >= 50:
                predictions = predictor.predict_group(recent_numbers, 10)
                self._report_progress(f"✅ Сгенерировано {len(predictions)} прогнозов")
                return predictions
        
        self._report_progress("⚠️ Не удалось сгенерировать прогнозы")
        return []
    
    def _analyze_model_performance(self, features_tensor: torch.Tensor, targets_tensor: torch.Tensor):
        """Анализ производительности модели с логированием"""
        self._report_progress("🔍 Запуск анализа производительности модели...")
        
        self.model.eval()
        with torch.no_grad():
            test_size = min(1000, len(features_tensor))
            test_features = features_tensor[:test_size]
            test_targets = targets_tensor[:test_size] + 1
            
            self._report_progress(f"📊 Тестирование на {test_size} примерах...")
            
            outputs = self.model(test_features)
            predictions = torch.argmax(outputs, dim=-1) + 1
            
            correct = (predictions == test_targets).float()
            accuracy = correct.mean().item()
            
            self._report_progress(f"📊 Accuracy на тестовых данных: {accuracy:.4f}")
            
            unique_predictions = len(torch.unique(predictions))
            self._report_progress(f"📊 Уникальных предсказанных чисел: {unique_predictions}/26")
    
    def _save_model(self):
        """Сохранение модели с логированием"""
        self._report_progress("💾 Сохранение модели на диск...")
        
        if self.model is not None:
            os.makedirs(os.path.dirname(self.model_path), exist_ok=True)
            torch.save({
                'model_state_dict': self.model.state_dict(),
                'model_config': {
                    'input_size': self.model.feature_extractor[0].in_features,
                    'hidden_size': self.model.feature_extractor[0].out_features
                }
            }, self.model_path)
            
            self._report_progress(f"✅ Модель сохранена: {self.model_path}")
        else:
            self._report_progress("❌ Не удалось сохранить модель: модель не инициализирована")
