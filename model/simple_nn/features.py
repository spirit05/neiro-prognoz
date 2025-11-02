# [file name]: model/simple_nn/features.py
"""
Извлечение features из истории чисел
"""

import numpy as np
from typing import List

class FeatureExtractor:
    def __init__(self, history_size: int = 20):
        self.history_size = history_size
    
    def extract_features(self, number_history: List[int]) -> np.ndarray:
        """Извлечение 50 features из истории чисел"""
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