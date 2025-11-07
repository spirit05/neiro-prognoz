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
                from ml.features.extractor import BaseFeatureExtractor  # ← ПРАВИЛЬНЫЙ ИМПОРТ
                self._feature_extractor = BaseFeatureExtractor(self.history_size)
            except ImportError as e:
                logger.error(f"❌ Не удалось загрузить BaseFeatureExtractor: {e}")
                # Создаем простой экстрактор на месте как fallback
                self._create_fallback_extractor()
        return self._feature_extractor
    
    def prepare_training_data(self, groups: List[str]) -> Tuple[np.ndarray, np.ndarray]:
        logger.info(f"🔍 DEBUG: Получено {len(groups)} групп")
        logger.info(f"🔍 DEBUG: Тип groups: {type(groups)}")
        logger.info(f"🔍 DEBUG: Тип первого элемента: {type(groups[0]) if groups else 'N/A'}")
        logger.info(f"🔍 DEBUG: Первые 3 группы: {groups[:3] if groups else 'N/A'}")
        
        all_numbers = []
        valid_groups = 0
        
        for i, group_str in enumerate(groups[:10]):  # Проверим только первые 10
            logger.info(f"🔍 DEBUG Группа {i}: '{group_str}' (тип: {type(group_str)})")
            if not isinstance(group_str, str):
                logger.warning(f"🔴 Группа {i} не строка: {type(group_str)}")
                continue
            try:
                numbers = [int(x) for x in group_str.strip().split()]
                logger.info(f"🔍 DEBUG Группа {i} числа: {numbers}")
                if len(numbers) == 4 and all(1 <= x <= 26 for x in numbers):
                    all_numbers.extend(numbers)
                    valid_groups += 1
                    logger.info(f"✅ Группа {i} валидна")
                else:
                    logger.warning(f"🟡 Группа {i} невалидна: {numbers}")
            except Exception as e:
                logger.error(f"🔴 Ошибка в группе {i}: {e}")
                continue
        
        logger.info(f"🔍 DEBUG: Валидных групп: {valid_groups}, всего чисел: {len(all_numbers)}")
        
        # ВРЕМЕННО уменьшим порог для теста
        if len(all_numbers) < 50:
            logger.error(f"❌ Недостаточно данных: {len(all_numbers)} чисел (нужно 50)")
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