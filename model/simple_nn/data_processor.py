# [file name]: model/simple_nn/data_processor.py
"""
Обработка данных для обучения
"""

import numpy as np
from typing import List, Tuple
from .features import FeatureExtractor

class DataProcessor:
    def __init__(self, history_size: int = 20):
        self.feature_extractor = FeatureExtractor(history_size)
        self.history_size = history_size
    
    def prepare_training_data(self, groups: List[str]) -> Tuple[np.ndarray, np.ndarray]:
        """Подготовка данных для обучения"""
        print("📊 Подготовка данных для упрощенной нейросети...")
        
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
        
        print(f"✅ Обработано {valid_groups} групп, {len(all_numbers)} чисел")
        
        if len(all_numbers) < self.history_size + 4:
            print(f"❌ Недостаточно данных для создания примеров")
            return np.array([]), np.array([])
        
        features = []
        targets = []
        
        for i in range(self.history_size, len(all_numbers) - 3):
            history = all_numbers[i - self.history_size:i]
            next_group = all_numbers[i:i + 4]
            
            feature_vector = self.feature_extractor.extract_features(history)
            features.append(feature_vector)
            targets.append(next_group)
        
        print(f"✅ Создано {len(features)} обучающих примеров")
        
        return np.array(features, dtype=np.float32), np.array(targets, dtype=np.int64)