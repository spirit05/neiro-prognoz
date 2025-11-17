# [file name]: ml/data/processors/data_processor.py
"""
Модульный Data Processor для новой архитектуры
ЧИСТАЯ АРХИТЕКТУРА БЕЗ ОБРАТНОЙ СОВМЕСТИМОСТИ
"""

import numpy as np
import pandas as pd
from typing import List, Tuple, Dict, Optional, Any
import logging

# 🔧 ИСПРАВЛЕНИЕ: Убираем импорт из ml.core.types чтобы избежать циклической зависимости
# Вместо этого создаем локальные классы для типов данных

class DataType:
    """Локальный enum для типов данных чтобы избежать циклического импорта"""
    TRAINING = "training"
    VALIDATION = "validation" 
    TESTING = "testing"
    PREDICTION = "prediction"

class SimpleDataBatch:
    """Упрощенный DataBatch чтобы избежать циклического импорта"""
    
    def __init__(self, data: pd.DataFrame, batch_id: str, data_type: str, metadata: Dict[str, Any] = None):
        self.data = data
        self.batch_id = batch_id
        self.data_type = data_type
        self.metadata = metadata or {}
    
    @property
    def empty(self) -> bool:
        return self.data.empty

# 🔧 ОСТАВЛЯЕМ импорты feature engineers - они безопасны
from ml.features.base import AbstractFeatureEngineer
from ml.features.engineers import StatisticalEngineer, AdvancedEngineer


class ModularDataProcessor:
    """
    Модульный процессор данных для новой архитектуры
    Использует StatisticalEngineer и AdvancedEngineer вместо BaseFeatureExtractor
    """
    
    def __init__(self, history_size: int = 20, feature_engineers: Optional[List[str]] = None):
        self.history_size = history_size
        self.logger = logging.getLogger(__name__)
        
        # Инициализация feature engineers
        self.feature_engineers: Dict[str, AbstractFeatureEngineer] = {}
        self._init_feature_engineers(feature_engineers or ["statistical", "advanced"])
        
        self.logger.info(f"✅ ModularDataProcessor инициализирован с {len(self.feature_engineers)} engineers")

    def _init_feature_engineers(self, engineer_names: List[str]) -> None:
        """Инициализация feature engineers"""
        for name in engineer_names:
            try:
                if name == "statistical":
                    self.feature_engineers[name] = StatisticalEngineer(self.history_size)
                elif name == "advanced":
                    self.feature_engineers[name] = AdvancedEngineer(self.history_size)
                else:
                    self.logger.warning(f"⚠️ Unknown feature engineer: {name}")
            except Exception as e:
                self.logger.error(f"❌ Ошибка инициализации {name}: {e}")

    def extract_features(self, number_history: List[int]) -> Dict[str, np.ndarray]:
        """Извлечение фич с использованием зарегистрированных engineers"""
        features = {}
        for name, engineer in self.feature_engineers.items():
            try:
                features[name] = engineer.extract_features(number_history)
                self.logger.debug(f"✅ Извлечено {len(features[name])} фич от {name}")
            except Exception as e:
                self.logger.error(f"❌ Ошибка извлечения фич {name}: {e}")
                features[name] = np.array([])
        
        return features

    def create_prediction_features(self, recent_groups: List[str]) -> SimpleDataBatch:
        """Создание фич для предсказания на основе последних групп"""
        try:
            # Извлекаем числа из последних групп
            recent_numbers = []
            for group_str in recent_groups:
                try:
                    numbers = [int(x) for x in group_str.strip().split()]
                    if len(numbers) == 4:
                        recent_numbers.extend(numbers)
                except Exception as e:
                    self.logger.warning(f"⚠️ Ошибка парсинга группы: {group_str}, {e}")
                    continue
            
            if len(recent_numbers) < self.history_size:
                self.logger.warning(f"⚠️ Недостаточно чисел: {len(recent_numbers)} < {self.history_size}")
                return self._create_empty_batch("prediction_insufficient_data")
            
            # Извлекаем фичи
            features_dict = self.extract_features(recent_numbers[-self.history_size:])
            
            # Комбинируем фичи в единый вектор
            combined_features = self._combine_features(features_dict)
            
            if combined_features.size == 0:
                return self._create_empty_batch("prediction_no_features")
            
            # Создаем SimpleDataBatch
            feature_df = pd.DataFrame([combined_features])
            
            return SimpleDataBatch(
                data=feature_df,
                batch_id=f"pred_{len(recent_groups)}_groups",
                data_type=DataType.PREDICTION,
                metadata={
                    "source_groups": recent_groups[-5:],  # последние 5 групп для отладки
                    "total_numbers": len(recent_numbers),
                    "feature_engineers_used": list(features_dict.keys())
                }
            )
            
        except Exception as e:
            self.logger.error(f"❌ Ошибка создания фич предсказания: {e}")
            return self._create_empty_batch("prediction_error")

    def prepare_training_data(self, groups: List[str]) -> Tuple[SimpleDataBatch, SimpleDataBatch]:
        """Подготовка данных для обучения"""
        try:
            # Валидация и парсинг групп
            all_numbers = []
            valid_groups = 0
            
            for i, group_str in enumerate(groups):
                if not isinstance(group_str, str):
                    continue
                try:
                    numbers = [int(x) for x in group_str.strip().split()]
                    if len(numbers) == 4 and all(1 <= x <= 26 for x in numbers):
                        all_numbers.extend(numbers)
                        valid_groups += 1
                except Exception:
                    continue
            
            self.logger.info(f"📊 Валидных групп: {valid_groups}, всего чисел: {len(all_numbers)}")
            
            # Проверка минимального количества данных
            if len(all_numbers) < 50:
                self.logger.error(f"❌ Недостаточно данных: {len(all_numbers)} чисел")
                return self._create_empty_batch("training_insufficient_data"), self._create_empty_batch("targets_insufficient_data")
            
            # Подготовка фич и таргетов
            features_list = []
            targets_list = []
            
            for i in range(self.history_size, len(all_numbers) - 3):
                history = all_numbers[i - self.history_size:i]
                next_group = all_numbers[i:i + 4]
                
                # Извлекаем фичи для истории
                features_dict = self.extract_features(history)
                combined_features = self._combine_features(features_dict)
                
                if combined_features.size > 0:
                    features_list.append(combined_features)
                    targets_list.append(next_group)
            
            if not features_list:
                self.logger.error("❌ Не удалось создать обучающие примеры")
                return self._create_empty_batch("training_no_examples"), self._create_empty_batch("targets_no_examples")
            
            # Создаем SimpleDataBatch для фич и таргетов
            features_df = pd.DataFrame(features_list)
            targets_df = pd.DataFrame(targets_list, columns=['target_1', 'target_2', 'target_3', 'target_4'])
            
            features_batch = SimpleDataBatch(
                data=features_df,
                batch_id=f"train_features_{len(features_list)}",
                data_type=DataType.TRAINING,
                metadata={
                    "total_examples": len(features_list),
                    "feature_dimension": combined_features.shape[0],
                    "feature_engineers": list(self.feature_engineers.keys())
                }
            )
            
            targets_batch = SimpleDataBatch(
                data=targets_df,
                batch_id=f"train_targets_{len(targets_list)}",
                data_type=DataType.TRAINING,
                metadata={
                    "total_targets": len(targets_list),
                    "target_columns": ['target_1', 'target_2', 'target_3', 'target_4']
                }
            )
            
            self.logger.info(f"✅ Создано {len(features_list)} обучающих примеров")
            return features_batch, targets_batch
            
        except Exception as e:
            self.logger.error(f"❌ Ошибка подготовки данных обучения: {e}")
            return self._create_empty_batch("training_error"), self._create_empty_batch("targets_error")

    def _combine_features(self, features_dict: Dict[str, np.ndarray]) -> np.ndarray:
        """Комбинация фич от разных engineers в единый вектор"""
        combined = []
        for name, features in features_dict.items():
            if features.size > 0:
                combined.extend(features.tolist())
        
        return np.array(combined, dtype=np.float32) if combined else np.array([], dtype=np.float32)

    def _create_empty_batch(self, batch_id: str) -> SimpleDataBatch:
        """Создание пустого SimpleDataBatch"""
        return SimpleDataBatch(
            data=pd.DataFrame(),
            batch_id=batch_id,
            data_type=DataType.PREDICTION,
            metadata={"empty": True, "reason": batch_id}
        )

    def get_feature_info(self) -> Dict[str, Any]:
        """Информация о feature engineers"""
        info = {
            "history_size": self.history_size,
            "active_engineers": list(self.feature_engineers.keys()),
            "feature_dimensions": {}
        }
        
        for name, engineer in self.feature_engineers.items():
            info["feature_dimensions"][name] = {
                "feature_count": len(engineer.get_feature_names()) if hasattr(engineer, 'get_feature_names') else "unknown",
                "engineer_type": type(engineer).__name__
            }
        
        return info
