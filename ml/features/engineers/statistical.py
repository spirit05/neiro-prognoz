# [file name]: ml/features/engineers/statistical.py
"""
Статистический feature engineer - миграция из FeatureExtractor
"""

import numpy as np
from typing import List
from ..base import AbstractFeatureEngineer

class StatisticalEngineer(AbstractFeatureEngineer):
    """Статистический feature engineer (миграция из FeatureExtractor)"""
    
    def __init__(self, history_size: int = 20):
        super().__init__(history_size)
        self._feature_names = self._generate_feature_names()
    
    def extract_features(self, number_history: List[int]) -> np.ndarray:
        """Извлечение 50 статистических features из истории чисел"""
        if len(number_history) == 0:
            return np.zeros(50, dtype=np.float32)
        
        history = np.array(number_history[-self.history_size:], dtype=np.float32)
        features = []
        
        # 1. Базовые статистики (6 features)
        features.extend([
            np.mean(history) / 26.0,
            np.std(history) / 26.0,
            np.min(history) / 26.0,
            np.max(history) / 26.0,
            np.median(history) / 26.0,
            len(set(history)) / len(history) if len(history) > 0 else 0.0,
        ])
        
        # 2. Частоты чисел 1-26 (26 features)
        freq = np.zeros(26)
        for num in history:
            if 1 <= num <= 26:
                freq[int(num) - 1] += 1
        if len(history) > 0:
            features.extend((freq / len(history)).tolist())
        else:
            features.extend([0.0] * 26)
        
        # 3. Скользящие статистики (6 features)
        if len(history) >= 5:
            recent_5 = history[-5:]
            features.extend([
                np.mean(recent_5) / 26.0,
                np.std(recent_5) / 26.0,
                np.median(recent_5) / 26.0,
            ])
        else:
            features.extend([0.0] * 3)
            
        if len(history) >= 10:
            recent_10 = history[-10:]
            features.extend([
                np.mean(recent_10) / 26.0,
                np.std(recent_10) / 26.0,
                np.median(recent_10) / 26.0,
            ])
        else:
            features.extend([0.0] * 3)
        
        # 4. Тренды и паттерны (8 features)
        if len(history) > 1:
            diffs = np.diff(history)
            features.extend([
                np.mean(diffs) / 25.0,
                np.std(diffs) / 25.0,
                np.sum(diffs > 0) / len(diffs),
                np.sum(diffs < 0) / len(diffs),
                np.sum(np.abs(diffs) > 10) / len(diffs),
            ])
            
            if len(history) >= 3:
                try:
                    autocorr = np.corrcoef(history[:-1], history[1:])[0,1]
                    features.append(max(0, autocorr) if not np.isnan(autocorr) else 0.0)
                except:
                    features.append(0.0)
            else:
                features.append(0.0)
                
            volatility = np.sum(np.abs(diffs)) / len(diffs) / 25.0
            features.extend([volatility, 1.0 - volatility])
        else:
            features.extend([0.0] * 8)
        
        # 5. Категориальные features (4 features)
        if len(history) > 0:
            even_count = sum(1 for x in history if x % 2 == 0)
            features.extend([
                even_count / len(history),
                1 - (even_count / len(history)),
                sum(1 for x in history if x <= 13) / len(history),
                sum(1 for x in history if x > 13) / len(history),
            ])
        else:
            features.extend([0.0] * 4)
        
        # Добиваем до 50 features если нужно
        while len(features) < 50:
            features.append(0.0)
        
        return np.array(features[:50], dtype=np.float32)
    
    def get_feature_names(self) -> List[str]:
        """Получение имен features"""
        return self._feature_names
    
    def _generate_feature_names(self) -> List[str]:
        """Генерация имен features"""
        names = []
        
        # Базовые статистики
        names.extend(['mean', 'std', 'min', 'max', 'median', 'unique_ratio'])
        
        # Частоты чисел
        names.extend([f'freq_{i+1}' for i in range(26)])
        
        # Скользящие статистики
        names.extend(['recent_5_mean', 'recent_5_std', 'recent_5_median'])
        names.extend(['recent_10_mean', 'recent_10_std', 'recent_10_median'])
        
        # Тренды и паттерны
        names.extend([
            'diff_mean', 'diff_std', 'diff_positive_ratio', 
            'diff_negative_ratio', 'diff_large_ratio', 'autocorr',
            'volatility', 'stability'
        ])
        
        # Категориальные
        names.extend(['even_ratio', 'odd_ratio', 'low_range_ratio', 'high_range_ratio'])
        
        # Дополняем если нужно
        while len(names) < 50:
            names.append(f'extra_{len(names)-50}')
        
        return names[:50]
