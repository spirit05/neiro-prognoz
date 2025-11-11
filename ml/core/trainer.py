# [file name]: ml/core/trainer.py
"""
Обучение УСИЛЕННОЙ нейросети - УПРОЩЕННАЯ ВЕРСИЯ как в старой архитектуре
"""

import torch
import torch.nn as nn
import torch.optim as optim
import numpy as np
from typing import List, Tuple
import os
import time
import gc
from config import paths, logging_config, constants
from ml.utils.data_utils import save_predictions

logger = logging_config.get_ml_system_logger()

class EnhancedTrainer:
    def __init__(self, model_path: str = None):
        self.model_path = model_path or paths.MODEL_FILE
        self.device = torch.device('cpu')
        self.model = None
        self.criterion = nn.CrossEntropyLoss()
        self.progress_callback = None
    
    def set_progress_callback(self, callback):
        """Установка callback для прогресса"""
        self.progress_callback = callback
    
    def _report_progress(self, message):
        """Отправка сообщения о прогрессе"""
        logger.info(message)
        if self.progress_callback:
            self.progress_callback(message)
   
    def train(self, groups: List[str], epochs=None, batch_size=None, learning_rate=None, is_finetune=False) -> List[Tuple[Tuple[int, int, int, int], float]]:
        """Обучение модели с ПРОСТЫМИ параметрами как в старой архитектуре"""
        from config.constants import MAIN_TRAINING_EPOCHS, MAIN_BATCH_SIZE, MAIN_LEARNING_RATE, HIDDEN_SIZE
        
        # 🔧 УПРОЩЕНИЕ: Используем параметры как в старой архитектуре
        if epochs is None:
            epochs = 15  # Меньше эпох для стабильности
        if batch_size is None:
            batch_size = 32  # Меньше batch_size
        if learning_rate is None:
            learning_rate = 0.001  # Стандартный learning rate
            
        total_start_time = time.time() 

        self._report_progress(f"🚀 ОБУЧЕНИЕ: {len(groups)} групп, {epochs} эпох")

        # Этап 1: Подготовка данных
        stage1_start = time.time()
        self._report_progress("📊 Этап 1: Подготовка данных...")

        from ml.core.data_processor import DataProcessor
        processor = DataProcessor(history_size=25)
        features, targets = processor.prepare_training_data(groups)

        stage1_time = time.time() - stage1_start
        self._report_progress(f"✅ Этап 1 завершен: {stage1_time:.1f} сек")

        if len(features) == 0:
            self._report_progress("❌ Не удалось подготовить данные для обучения")
            return []

        if len(features) < 20:
            self._report_progress(f"⚠️ Мало данных: {len(features)} примеров")
            return []

        self._report_progress(f"✅ Создано {len(features)} обучающих примеров")

        # Этап 2: Создание модели
        stage2_start = time.time()
        self._report_progress("🔧 Этап 2: Создание модели...")

        if self.model is None:
            from ml.core.model import EnhancedNumberPredictor
            # 🔧 ИСПРАВЛЕНИЕ: Используем input_size из данных
            input_size = features.shape[1]
            self.model = EnhancedNumberPredictor(input_size=input_size, hidden_size=128)
            self._report_progress(f"✅ Создана новая модель: input_size={input_size}")
        else:
            self._report_progress("🔄 Используем существующую модель")

        stage2_time = time.time() - stage2_start
        self._report_progress(f"✅ Этап 2 завершен: {stage2_time:.1f} сек")

        # Этап 3: Настройка оптимизатора
        stage3_start = time.time()
        self._report_progress("⚙️ Этап 3: Настройка оптимизатора...")

        # 🔧 УПРОЩЕНИЕ: Простой Adam оптимизатор как в старой архитектуре
        self.optimizer = optim.Adam(self.model.parameters(), lr=learning_rate)
        # 🔧 УБИРАЕМ сложный scheduler для стабильности

        stage3_time = time.time() - stage3_start
        self._report_progress(f"✅ Этап 3 завершен: {stage3_time:.1f} сек")

        features_tensor = torch.tensor(features, dtype=torch.float32)
        targets_tensor = torch.tensor(targets, dtype=torch.long) - 1  # Для CrossEntropy

        # Этап 4: Обучение модели
        stage4_start = time.time()
        self._report_progress("🧠 Этап 4: Обучение модели...")

        self.model.train()
        best_loss = float('inf')

        for epoch in range(epochs):
            epoch_start_time = time.time()
            # 🔧 УПРОЩЕНИЕ: Простой цикл обучения без shuffling для стабильности
            total_loss = 0
            num_batches = 0

            for i in range(0, len(features), batch_size):
                batch_start = i
                batch_end = min(i + batch_size, len(features))
                if batch_end - batch_start < 2:
                    continue

                batch_features = features_tensor[batch_start:batch_end]
                batch_targets = targets_tensor[batch_start:batch_end]

                self.optimizer.zero_grad()
                outputs = self.model(batch_features)

                # 🔧 ИСПРАВЛЕНИЕ: Простой расчет loss
                loss = 0
                for pos in range(4):
                    loss += self.criterion(outputs[:, pos, :], batch_targets[:, pos])
                loss = loss / 4

                loss.backward()
                self.optimizer.step()

                total_loss += loss.item()
                num_batches += 1

            epoch_time = time.time() - epoch_start_time

            if num_batches > 0:
                avg_loss = total_loss / num_batches
                self._report_progress(f"📈 Эпоха {epoch+1}/{epochs}, Loss: {avg_loss:.4f}, Время: {epoch_time:.1f} сек")

                if avg_loss < best_loss:
                    best_loss = avg_loss
                    self._save_model()
                    self._report_progress(f"💾 Сохранена лучшая модель (loss: {avg_loss:.4f})")

        stage4_time = time.time() - stage4_start
        self._report_progress(f"✅ Этап 4 завершен: {stage4_time:.1f} сек")
        self._report_progress(f"✅ Обучение завершено! Лучший loss: {best_loss:.4f}")

        # Сохраняем финальную модель
        self._save_model()

        # Генерация прогнозов после обучения
        predictions = self._generate_predictions_after_training(groups)
        
        total_time = time.time() - total_start_time
        self._report_progress(f"🎉 ВСЕ ЭТАПЫ ЗАВЕРШЕНЫ! Общее время: {total_time:.1f} сек")

        return predictions
    
    def _generate_predictions_after_training(self, groups: List[str]) -> List[Tuple[Tuple[int, int, int, int], float]]:
        """Генерация прогнозов после обучения - УПРОЩЕННАЯ ВЕРСИЯ"""
        predictions = []
        try:
            if self.model is not None:
                self.model.eval()
                from ml.core.data_processor import DataProcessor
                processor = DataProcessor(history_size=25)
                recent_groups = groups[-25:] if len(groups) >= 25 else groups

                context_features = processor.create_prediction_features(recent_groups)

                if context_features is not None and len(context_features) > 0:
                    with torch.no_grad():
                        features_tensor = torch.tensor(context_features, dtype=torch.float32)
                        outputs = self.model(features_tensor)
                        
                        # 🔧 ИСПРАВЛЕНИЕ: Простая генерация прогнозов
                        for i in range(min(5, len(outputs))):
                            predicted_numbers = []
                            confidence = 1.0
                            for pos in range(4):
                                probs = torch.softmax(outputs[i, pos, :], dim=0)
                                predicted_num = torch.argmax(probs).item() + 1
                                predicted_numbers.append(predicted_num)
                                confidence *= probs[predicted_num - 1].item()
                            
                            # 🔧 Проверяем что числа разные
                            if len(set(predicted_numbers)) >= 3:  # Хотя бы 3 разных числа
                                predictions.append((tuple(predicted_numbers), confidence))
                        
                        # Если не получилось сгенерировать хорошие прогнозы, создаем базовые
                        if not predictions:
                            self._report_progress("⚠️  Создаем базовые прогнозы...")
                            predictions = self._create_basic_predictions()
                            
        except Exception as e:
            self._report_progress(f"❌ Ошибка генерации прогнозов: {e}")
            predictions = self._create_basic_predictions()

        self._report_progress(f"✅ Сгенерировано {len(predictions)} прогнозов")
        return predictions
    
    def _create_basic_predictions(self) -> List[Tuple[Tuple[int, int, int, int], float]]:
        """Создание базовых прогнозов при проблемах с моделью"""
        import random
        predictions = []
        for i in range(4):
            # Создаем группу с разными числами
            while True:
                group = tuple(random.sample(range(1, 27), 4))
                if len(set(group)) == 4:  # Все числа разные
                    predictions.append((group, 0.001))
                    break
        return predictions
        
    def _save_model(self):
        """Сохранение модели"""
        self._report_progress("💾 Сохранение модели на диск...")
        
        if self.model is not None:
            os.makedirs(os.path.dirname(self.model_path), exist_ok=True)
            torch.save({
                'model_state_dict': self.model.state_dict(),
                'model_config': {
                    'input_size': self.model.input_size,
                    'hidden_size': self.model.hidden_size
                }
            }, self.model_path)
            
            self._report_progress(f"✅ Модель сохранена: {self.model_path}")
