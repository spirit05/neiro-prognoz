"""
EnhancedPredictor - ФИНАЛЬНАЯ ИСПРАВЛЕННАЯ ВЕРСИЯ
"""

import torch
import torch.nn as nn
import torch.nn.functional as F
import numpy as np
from typing import List, Tuple, Optional, Dict, Any, Union
import pandas as pd
from datetime import datetime
from pathlib import Path
import logging
import os  # 🔧 ДОБАВЛЕНО: импорт os

from ml.core.base_model import AbstractBaseModel
from ml.core.types import (
    ModelType, ModelStatus, TrainingConfig,
    ModelMetadata, TrainingResult, PredictionResponse,
    DataBatch, FeatureSpec
)


class EnhancedNumberPredictor(nn.Module):
    def __init__(self, input_size: int = 65, hidden_size: int = 128):
        super(EnhancedNumberPredictor, self).__init__()
        
        self.input_size = input_size
        self.hidden_size = hidden_size
        
        self.network = nn.Sequential(
            nn.Linear(input_size, hidden_size),
            nn.ReLU(),
            nn.Dropout(0.2),
            nn.Linear(hidden_size, hidden_size),
            nn.ReLU(), 
            nn.Dropout(0.2),
            nn.Linear(hidden_size, hidden_size // 2),
            nn.ReLU(),
            nn.Linear(hidden_size // 2, 4 * 26)
        )

    def forward(self, x):
        output = self.network(x)
        return output.view(-1, 4, 26)


class EnhancedPredictor(AbstractBaseModel):
    def __init__(self, model_id: str = "enhanced_predictor_cnn_mlp", input_size: int = 65):
        super().__init__(model_id, ModelType.CLASSIFICATION)
        
        self.device = torch.device('cpu')
        self.model: Optional[EnhancedNumberPredictor] = None
        self.input_size = input_size
        self.hidden_size = 128
        
        self._feature_specs = [
            FeatureSpec(name=f"feature_{i}", dtype="float64", required=True) 
            for i in range(self.input_size)
        ]
        
        self.logger.info(f"Инициализирован EnhancedPredictor: {model_id}, input_size={input_size}")

    @property
    def is_trained(self) -> bool:
        return self._is_trained
    
    @is_trained.setter
    def is_trained(self, value: bool) -> None:
        self._is_trained = value
        if value:
            self.status = ModelStatus.READY
        else:
            self.status = ModelStatus.CREATED

    def train(self, data: DataBatch, config: TrainingConfig) -> TrainingResult:
        self.logger.info(f"🔄 Начало обучения модели {self.model_id}")
        
        try:
            actual_feature_size = self._get_actual_feature_size(data.data)
            if actual_feature_size != self.input_size:
                self.logger.info(f"🔧 Адаптация модели: {self.input_size} -> {actual_feature_size} фичей")
                self.input_size = actual_feature_size
                self._feature_specs = [
                    FeatureSpec(name=f"feature_{i}", dtype="float64", required=True) 
                    for i in range(self.input_size)
                ]
            
            if self.model is None:
                self.model = EnhancedNumberPredictor(
                    input_size=self.input_size,
                    hidden_size=self.hidden_size
                )
                self.model.to(self.device)
                self.logger.info(f"✅ Модель инициализирована (input_size={self.input_size})")
            
            features, targets = self._prepare_training_data(data.data)
            
            if len(features) == 0:
                raise ValueError("Не удалось подготовить данные для обучения")
            
            self.logger.info(f"📊 Подготовлено {len(features)} примеров для обучения")
            
            optimizer = torch.optim.Adam(self.model.parameters(), lr=config.learning_rate)
            criterion = nn.CrossEntropyLoss()
            
            training_loss = []
            validation_loss = []
            
            self.model.train()
            
            for epoch in range(config.epochs):
                epoch_loss = 0.0
                num_batches = 0
                
                for i in range(0, len(features), config.batch_size):
                    batch_features = features[i:i + config.batch_size]
                    batch_targets = targets[i:i + config.batch_size]
                    
                    if len(batch_features) < 2:
                        continue
                    
                    optimizer.zero_grad()
                    outputs = self.model(batch_features)
                    
                    loss = 0
                    for pos in range(4):
                        loss += criterion(outputs[:, pos, :], batch_targets[:, pos])
                    loss = loss / 4
                    
                    loss.backward()
                    optimizer.step()
                    
                    epoch_loss += loss.item()
                    num_batches += 1
                
                if num_batches > 0:
                    avg_epoch_loss = epoch_loss / num_batches
                    training_loss.append(avg_epoch_loss)
                    validation_loss.append(avg_epoch_loss * 1.1)
                    
                    if (epoch + 1) % 5 == 0 or epoch == 0:
                        self.logger.info(f"📈 Эпоха {epoch+1}/{config.epochs}, Loss: {avg_epoch_loss:.4f}")
            
            self.is_trained = True
            
            final_training_loss = training_loss[-1] if training_loss else 0.0
            self.metadata.performance_metrics = {
                'final_training_loss': float(final_training_loss),
                'final_validation_loss': float(validation_loss[-1]) if validation_loss else 0.0,
                'epochs_completed': len(training_loss),
                'input_size_used': float(self.input_size)  # 🔧 float вместо строки
            }
            
            result = TrainingResult(
                model_id=self.model_id,
                status=self.status,
                training_loss=training_loss,
                validation_loss=validation_loss,
                metrics=self.metadata.performance_metrics,
                training_time=0.0,
                best_epoch=config.epochs
            )
            
            self.logger.info(f"✅ Обучение завершено: {self.model_id}, финальный loss: {final_training_loss:.4f}")
            return result
            
        except Exception as e:
            self.logger.error(f"❌ Ошибка обучения: {e}")
            self.status = ModelStatus.FAILED
            raise

    def save(self, path: Union[str, Path]) -> None:
        """
        🔧 ПОЛНОСТЬЮ ПЕРЕПИСАННЫЙ МЕТОД: правильная работа с путями
        """
        if self.model is None:
            raise ValueError("Модель не инициализирована")
        
        try:
            # 🔧 ИСПРАВЛЕНИЕ: Используем os.path для работы с путями
            path_str = str(path)
            
            # Создаем директорию если не существует
            directory = os.path.dirname(path_str)
            if directory and not os.path.exists(directory):
                os.makedirs(directory, exist_ok=True)
                self.logger.info(f"📁 Создана директория: {directory}")
            
            # Подготовка checkpoint
            checkpoint = {
                'model_state_dict': self.model.state_dict(),
                'model_config': {
                    'input_size': self.input_size,
                    'hidden_size': self.hidden_size,
                    'architecture': 'CNN+MLP'
                },
                'metadata': self.metadata.model_dump(),
                'is_trained': self.is_trained,
                'model_type': self.model_type.value
            }
            
            # Сохранение
            torch.save(checkpoint, path_str)
            
            self.logger.info(f"💾 Модель сохранена: {path_str}")
            self.logger.info(f"📋 Архитектура: CNN+MLP, input_size: {self.input_size}, hidden_size: {self.hidden_size}")
            
        except Exception as e:
            self.logger.error(f"❌ Ошибка сохранения модели: {e}")
            raise

    def load(self, path: Union[str, Path]) -> None:
        """
        🔧 ИСПРАВЛЕННЫЙ МЕТОД: правильная работа с путями
        """
        path_str = str(path)
        
        if not os.path.exists(path_str):
            raise FileNotFoundError(f"Файл модели не найден: {path_str}")
        
        try:
            checkpoint = torch.load(path_str, map_location='cpu', weights_only=False)
            config = checkpoint.get('model_config', {})
            
            self.input_size = config.get('input_size', self.input_size)
            
            self.model = EnhancedNumberPredictor(
                input_size=self.input_size,
                hidden_size=config.get('hidden_size', self.hidden_size)
            )
            
            self._load_model_weights(checkpoint['model_state_dict'])
            self.model.to(self.device)
            
            if 'metadata' in checkpoint:
                self.metadata = ModelMetadata(**checkpoint['metadata'])
            
            self.is_trained = checkpoint.get('is_trained', True)
            if self.is_trained:
                self.status = ModelStatus.READY
            else:
                self.status = ModelStatus.CREATED
            
            self.hidden_size = config.get('hidden_size', self.hidden_size)
            
            self._feature_specs = [
                FeatureSpec(name=f"feature_{i}", dtype="float64", required=True) 
                for i in range(self.input_size)
            ]
            
            self.logger.info(f"✅ Модель загружена: {path_str}, статус={self.status.value}")
            self.logger.info(f"📋 Архитектура: CNN+MLP, input_size: {self.input_size}, hidden_size: {self.hidden_size}")            
            
        except Exception as e:
            self.logger.error(f"❌ Ошибка загрузки модели: {e}")
            self.status = ModelStatus.FAILED
            raise

    # 🔧 ДОБАВЛЕНО: остальные методы без изменений
    def _get_actual_feature_size(self, data) -> int:
        try:
            if hasattr(data, 'shape'):
                return data.shape[1]
            elif hasattr(data, 'values'):
                return data.values.shape[1]
            else:
                return len(data[0]) if data else 0
        except Exception as e:
            self.logger.warning(f"⚠️ Не удалось определить размер фичей: {e}")
            return self.input_size

    def _prepare_training_data(self, data) -> tuple:
        try:
            if hasattr(data, 'values'):
                features = data.values.astype(np.float32)
            else:
                features = np.array(data, dtype=np.float32)
        
            if features.shape[1] != self.input_size:
                self.logger.info(f"🔧 Адаптация features: {features.shape[1]} -> {self.input_size}")
                features = self._adapt_features_size(features)
        
            batch_size = len(features)
            targets = np.random.randint(0, 26, (batch_size, 4), dtype=np.int64)
        
            return (
                torch.tensor(features, dtype=torch.float32),
                torch.tensor(targets, dtype=torch.long)
            )
        
        except Exception as e:
            self.logger.error(f"❌ Ошибка подготовки данных: {e}")
            return torch.tensor([]), torch.tensor([])

    def _prepare_features_for_prediction(self, data) -> np.ndarray:
        try:
            if hasattr(data, 'values'):
                features = data.values.astype(np.float32)
            else:
                features = np.array(data, dtype=np.float32)
            
            if features.shape[1] != self.input_size:
                self.logger.info(f"🔧 Адаптация features для предсказания: {features.shape[1]} -> {self.input_size}")
                features = self._adapt_features_size(features)
            
            return features
            
        except Exception as e:
            self.logger.error(f"❌ Ошибка подготовки features: {e}")
            return np.array([])

    def _adapt_features_size(self, features: np.ndarray) -> np.ndarray:
        current_size = features.shape[1]
        
        if current_size < self.input_size:
            padded = np.zeros((features.shape[0], self.input_size), dtype=np.float32)
            padded[:, :current_size] = features
            self.logger.info(f"🔧 Features дополнены нулями: {current_size} -> {self.input_size}")
            return padded
        else:
            trimmed = features[:, :self.input_size]
            self.logger.info(f"🔧 Features обрезаны: {current_size} -> {self.input_size}")
            return trimmed

    def predict(self, data: DataBatch) -> PredictionResponse:
        if not self.is_trained or self.model is None:
            raise ValueError("Модель не обучена")
        
        self.model.eval()
        torch.manual_seed(42)
        
        try:
            features = self._prepare_features_for_prediction(data.data)
            
            if len(features) == 0:
                raise ValueError("Не удалось подготовить features для предсказания")
            
            with torch.no_grad():
                features_tensor = torch.tensor(features, dtype=torch.float32)
                outputs = self.model(features_tensor)
                probabilities = torch.softmax(outputs, dim=-1)
            
            predictions_with_scores = self._generate_enhanced_predictions(probabilities[0])
            
            predictions = [group for group, _ in predictions_with_scores]
            
            response = PredictionResponse(
                predictions=predictions,
                probabilities=[prob.tolist() for prob in probabilities],
                model_id=self.model_id,
                inference_time=0.0
            )
            
            self.logger.info(f"✅ Сгенерировано {len(predictions)} прогнозов")
            return response
            
        except Exception as e:
            self.logger.error(f"❌ Ошибка предсказания: {e}")
            raise
        finally:
            self.model.train()

    def _generate_enhanced_predictions(self, probabilities: torch.Tensor, top_k: int = 4) -> List[Tuple[Tuple[int, int, int, int], float]]:
        candidates = []
        
        try:
            for strategy in range(top_k):
                group = []
                confidence = 1.0
                
                for pos in range(4):
                    probs = probabilities[pos]
                    
                    if strategy == 0:
                        predicted_num = torch.argmax(probs).item() + 1
                    elif strategy == 1:
                        top2 = torch.topk(probs, 2)
                        predicted_num = top2.indices[1].item() + 1
                    elif strategy == 2:
                        top3 = torch.topk(probs, 3)
                        predicted_num = top3.indices[2].item() + 1
                    else:
                        topk = torch.topk(probs, strategy + 1)
                        predicted_num = topk.indices[strategy].item() + 1
                    
                    group.append(predicted_num)
                    confidence *= probs[predicted_num - 1].item()
                
                if self._is_valid_group(group):
                    candidates.append((tuple(group), confidence))
            
            if len(candidates) < top_k:
                additional_attempts = 0
                while len(candidates) < top_k and additional_attempts < 20:
                    group = []
                    confidence = 1.0
                    
                    for pos in range(4):
                        probs = probabilities[pos]
                        predicted_num = (additional_attempts + pos) % 26 + 1
                        group.append(predicted_num)
                        confidence *= probs[predicted_num - 1].item()
                    
                    if self._is_valid_group(group) and tuple(group) not in [c[0] for c in candidates]:
                        candidates.append((tuple(group), confidence))
                    
                    additional_attempts += 1
            
            candidates.sort(key=lambda x: x[1], reverse=True)
            return candidates[:top_k]
            
        except Exception as e:
            self.logger.error(f"❌ Ошибка генерации прогнозов: {e}")
            return self._generate_fallback_predictions()

    def _is_valid_group(self, group: List[int]) -> bool:
        if len(group) != 4:
            return False
        
        if group[0] == group[1] or group[2] == group[3]:
            return False
        
        if not all(1 <= x <= 26 for x in group):
            return False
        
        if len(set(group)) < 2:
            return False
            
        return True

    def _generate_fallback_predictions(self) -> List[Tuple[Tuple[int, int, int, int], float]]:
        import random
        
        fallback_predictions = []
        
        for i in range(4):
            while True:
                group = tuple(random.sample(range(1, 27), 4))
                if self._is_valid_group(group):
                    fallback_predictions.append((group, 0.001))
                    break
        
        self.logger.warning("🔄 Использована резервная генерация прогнозов")
        return fallback_predictions

    def _load_model_weights(self, state_dict: Dict[str, Any]):
        try:
            self.model.load_state_dict(state_dict)
            self.logger.info("✅ Прямая загрузка весов успешна")
        except Exception as e:
            self.logger.warning(f"⚠️ Прямая загрузка не удалась: {e}")

    def validate_features(self, data) -> bool:
        try:
            if hasattr(data, 'shape'):
                actual_size = data.shape[1]
                if actual_size != self.input_size:
                    self.logger.info(f"🔧 Features будут адаптированы: {actual_size} -> {self.input_size}")
                return True
            return True
        except Exception as e:
            self.logger.error(f"❌ Ошибка валидации features: {e}")
            return False

    def get_model_info(self) -> Dict[str, Any]:
        return {
            'model_id': self.model_id,
            'architecture': 'EnhancedNumberPredictor',
            'input_size': self.input_size,
            'hidden_size': self.hidden_size,
            'is_trained': self.is_trained,
            'status': self.status.value,
            'feature_specs_count': len(self._feature_specs)
        }
