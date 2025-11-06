"""
Обработка данных для обучения - МОДУЛЬНАЯ АРХИТЕКТУРА
"""

import numpy as np
from typing import List, Tuple
from config import paths, logging_config

logger = logging_config.get_ml_system_logger()

class DataProcessor:
    def __init__(self, history_size: int = 20):
        self.history_size = history_size
        self._feature_extractor = None
    
    def _get_feature_extractor(self):
        """Ленивая загрузка FeatureExtractor"""
        if self._feature_extractor is None:
            try:
                from ml.features.extractor import FeatureExtractor
                self._feature_extractor = FeatureExtractor(self.history_size)
            except ImportError as e:
                logger.error(f"❌ Не удалось загрузить FeatureExtractor: {e}")
                # Fallback на базовый экстрактор
                from ml.features.extractor import BaseFeatureExtractor
                self._feature_extractor = BaseFeatureExtractor(self.history_size)
        return self._feature_extractor
    
    def prepare_training_data(self, groups: List[str]) -> Tuple[np.ndarray, np.ndarray]:
        """Подготовка данных для обучения"""
        logger.info("📊 Подготовка данных для упрощенной нейросети...")
        
        all_numbers = []
        valid_groups = 0
        
        for group_str in groups:
            if not isinstance(group_str, str):
                continue
            try:
                numbers = [int(x) for x in group_str.strip().split()]
                if len(numbers) == 4 and all(1 <= x <= 26 for x in numbers):
                    all_numbers.extend(numbers)
                    valid_groups += 1
            except:
                continue
        
        logger.info(f"✅ Обработано {valid_groups} групп, {len(all_numbers)} чисел")
        
        if len(all_numbers) < self.history_size + 4:
            logger.error(f"❌ Недостаточно данных для создания примеров")
            return np.array([]), np.array([])
        
        features = []
        targets = []
        feature_extractor = self._get_feature_extractor()
        
        for i in range(self.history_size, len(all_numbers) - 3):
            history = all_numbers[i - self.history_size:i]
            next_group = all_numbers[i:i + 4]
            
            feature_vector = feature_extractor.extract_features(history)
            features.append(feature_vector)
            targets.append(next_group)
        
        logger.info(f"✅ Создано {len(features)} обучающих примеров")
        
        return np.array(features, dtype=np.float32), np.array(targets, dtype=np.int64)