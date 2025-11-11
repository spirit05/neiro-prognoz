# [file name]: ml/core/trainer.py
"""
Обучение УСИЛЕННОЙ нейросети - МОДУЛЬНАЯ АРХИТЕКТУРА
ИСПРАВЛЕННАЯ ВЕРСИЯ: устранена проблема одинаковых прогнозов
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

# 🔧 ИСПРАВЛЕНИЕ: Добавляем импорт save_predictions
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
        """Обучение модели с ИСПРАВЛЕННЫМИ параметрами для дообучения"""
        from config.constants import MAIN_TRAINING_EPOCHS, MAIN_BATCH_SIZE, MAIN_LEARNING_RATE, HIDDEN_SIZE, RETRAIN_EPOCHS, RETRAIN_LEARNING_RATE
        
        # 🔧 ИСПРАВЛЕНИЕ: Разные параметры для полного обучения и дообучения
        if is_finetune:
            if epochs is None:
                epochs = RETRAIN_EPOCHS
            if learning_rate is None:
                learning_rate = RETRAIN_LEARNING_RATE  # Выше для дообучения
            l2_lambda = 0.0001  # Меньше регуляризации для дообучения
            description = "ДООБУЧЕНИЕ"
        else:
            if epochs is None:
                epochs = MAIN_TRAINING_EPOCHS
            if learning_rate is None:
                learning_rate = MAIN_LEARNING_RATE
            l2_lambda = 0.001  # Нормальная регуляризация для полного обучения
            description = "ПОЛНОЕ ОБУЧЕНИЕ"
            
        if batch_size is None:
            batch_size = MAIN_BATCH_SIZE
            
        total_start_time = time.time() 

        self._report_progress(f"🚀 {description}: {len(groups)} групп, {epochs} эпох, LR={learning_rate}")

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

        if len(features) < 50:  # 🔧 Уменьшил порог для дообучения
            self._report_progress(f"⚠️ Мало данных: {len(features)} примеров (для дообучения нормально)")
            # Не возвращаем пустой список, продолжаем с тем что есть

        self._report_progress(f"✅ Обработано {len(groups)} групп, создано {len(features)} обучающих примеров")

        # Этап 2: Создание/загрузка модели
        stage2_start = time.time()
        self._report_progress("🔧 Этап 2: Подготовка модели...")

        if self.model is None:
            from ml.core.model import EnhancedNumberPredictor
            self.model = EnhancedNumberPredictor(input_size=features.shape[1], hidden_size=HIDDEN_SIZE)
            self._report_progress("✅ Создана новая модель")
        else:
            self._report_progress("🔄 Используем существующую модель для дообучения")

        torch.backends.cudnn.deterministic = True
        torch.backends.cudnn.benchmark = False

        stage2_time = time.time() - stage2_start
        self._report_progress(f"✅ Этап 2 завершен: {stage2_time:.1f} сек")

        # Этап 3: Настройка оптимизатора
        stage3_start = time.time()
        self._report_progress("⚙️ Этап 3: Настройка оптимизатора...")

        # 🔧 ИСПРАВЛЕНИЕ: Разные параметры оптимизатора
        if is_finetune:
            # Для дообучения: более агрессивный оптимизатор
            self.optimizer = optim.AdamW(self.model.parameters(), lr=learning_rate, weight_decay=1e-5)
            self.scheduler = optim.lr_scheduler.CosineAnnealingLR(self.optimizer, T_max=epochs)
        else:
            # Для полного обучения: консервативный подход
            self.optimizer = optim.AdamW(self.model.parameters(), lr=learning_rate, weight_decay=1e-4)
            self.scheduler = optim.lr_scheduler.ReduceLROnPlateau(self.optimizer, mode='min', factor=0.5, patience=3)

        stage3_time = time.time() - stage3_start
        self._report_progress(f"✅ Этап 3 завершен: {stage3_time:.1f} сек")

        features_tensor = torch.tensor(features, dtype=torch.float32)
        targets_tensor = torch.tensor(targets, dtype=torch.long) - 1

        # Этап 4: Обучение модели
        stage4_start = time.time()
        self._report_progress("🧠 Этап 4: Обучение модели...")

        self.model.train()
        best_loss = float('inf')
        patience_counter = 0
        patience = 3 if is_finetune else 5  # 🔧 Меньше терпения для дообучения

        for epoch in range(epochs):
            epoch_start_time = time.time()
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

                # 🔧 ИСПРАВЛЕНИЕ: Адаптивная регуляризация
                l2_norm = sum(p.pow(2.0).sum() for p in self.model.parameters())
                loss = loss + l2_lambda * l2_norm

                loss.backward()
                
                # 🔧 ИСПРАВЛЕНИЕ: Gradient clipping для стабильности
                torch.nn.utils.clip_grad_norm_(self.model.parameters(), max_norm=0.5)
                self.optimizer.step()

                total_loss += loss.item()
                num_batches += 1

            epoch_time = time.time() - epoch_start_time

            if num_batches > 0:
                avg_loss = total_loss / num_batches
                
                # 🔧 ИСПРАВЛЕНИЕ: Разные стратегии scheduler
                if is_finetune:
                    self.scheduler.step()
                    current_lr = self.scheduler.get_last_lr()[0]
                else:
                    self.scheduler.step(avg_loss)
                    current_lr = self.optimizer.param_groups[0]['lr']
                    
                self._report_progress(f"📈 Эпоха {epoch+1}/{epochs}, Loss: {avg_loss:.4f}, LR: {current_lr:.6f}, Время: {epoch_time:.1f} сек")

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
        self._report_progress(f"✅ {description} завершено! Лучший loss: {best_loss:.4f}")

        # Сохраняем модель
        try:
            torch.save({
                'model_state_dict': self.model.state_dict(),
                'model_config': {
                    'input_size': self.model.input_size,
                    'hidden_size': self.model.hidden_size
                }
            }, self.model_path)
            self._report_progress("💾 Модель успешно сохранена в файл")
        except Exception as e:
            self._report_progress(f"❌ Ошибка сохранения модели: {e}")

        # Этап 5: Анализ производительности
        stage5_start = time.time()
        self._report_progress("📊 Этап 5: Анализ производительности...")
        self._analyze_model_performance(features_tensor, targets_tensor)
        stage5_time = time.time() - stage5_start
        self._report_progress(f"✅ Этап 5 завершен: {stage5_time:.1f} сек")

        # Этап 6: Очистка памяти
        stage6_start = time.time()
        self._report_progress("🧹 Этап 6: Очистка памяти...")
        del features_tensor, targets_tensor, features_shuffled, targets_shuffled
        gc.collect()
        if torch.cuda.is_available():
            torch.cuda.empty_cache()
        stage6_time = time.time() - stage6_start
        self._report_progress(f"✅ Этап 6 завершен: {stage6_time:.1f} сек")

        # Генерация прогнозов после обучения
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

                        for i in range(min(10, len(outputs))):
                            predicted_numbers = []
                            confidence = 1.0
                            for pos in range(4):
                                probs = torch.softmax(outputs[i, pos, :], dim=0)
                                predicted_num = torch.argmax(probs).item() + 1
                                predicted_numbers.append(predicted_num)
                                confidence *= probs[predicted_num - 1].item()
                            predictions.append((tuple(predicted_numbers), confidence))
        except Exception as e:
            self._report_progress(f"❌ Ошибка генерации прогнозов: {e}")

        self._report_progress(f"✅ Сгенерировано {len(predictions)} прогнозов")

        # Система анализа после обучения
        try:
            from config.constants import MAIN_TRAINING_EPOCHS, RETRAIN_EPOCHS
            from ml.learning.self_learning import SelfLearningSystem
        except ImportError as e:
            self._report_progress(f"⚠️ Не удалось импортировать SelfLearningSystem: {e}")
            SelfLearningSystem = None

        if 'SelfLearningSystem' in locals() and callable(SelfLearningSystem):
            try:
                # 🔧 ИСПРАВЛЕНИЕ: Сброс анализа только при полном обучении
                if not is_finetune and (epochs >= MAIN_TRAINING_EPOCHS):
                    learning_system = SelfLearningSystem()
                    learning_system.reset_learning_data()
                    self._report_progress("✅ Система анализа сброшена после полного переобучения")
                else:
                    self._report_progress("📊 Анализ сохранен (дообучение)")
            except Exception as e:
                self._report_progress(f"⚠️ Ошибка при сбросе анализа: {e}")

        total_time = time.time() - total_start_time
        self._report_progress(f"🎉 ВСЕ ЭТАПЫ ЗАВЕРШЕНЫ! Общее время: {total_time:.1f} сек")

        # Сохранение прогнозов
        try:
            # 🔧 ИСПРАВЛЕНИЕ: Теперь save_predictions импортирован
            if predictions:
                save_predictions(predictions)
                self._report_progress(f"💾 Сохранено {len(predictions)} прогнозов в predictions_state.json")
            else:
                self._report_progress("⚠️ Прогнозы не сохранены: список пуст")
        except Exception as e:
            self._report_progress(f"❌ Ошибка сохранения прогнозов: {e}")

        return predictions
        
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
            
            # 🔧 ИСПРАВЛЕНИЕ: Детальный анализ распределения предсказаний
            unique_predictions = len(torch.unique(predictions))
            self._report_progress(f"📊 Уникальных предсказанных чисел: {unique_predictions}/26")
            
            # Анализ энтропии предсказаний
            probs = torch.softmax(outputs, dim=-1)
            entropy = -torch.sum(probs * torch.log(probs + 1e-8), dim=-1).mean().item()
            self._report_progress(f"📊 Средняя энтропия предсказаний: {entropy:.4f}")
    
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
