# [file name]: ml/features/engineers/advanced.py
"""
Продвинутый feature engineer - миграция из AdvancedPatternAnalyzer
"""

import numpy as np
from scipy import stats
from typing import List, Dict
from ..base import AbstractFeatureEngineer

class AdvancedEngineer(AbstractFeatureEngineer):
    """Продвинутый feature engineer для анализа временных рядов"""
    
    def __init__(self, history_size: int = 20):
        super().__init__(history_size)
        self._feature_names = self._generate_feature_names()
    
    def extract_features(self, number_history: List[int]) -> np.ndarray:
        """Извлечение продвинутых features для анализа паттернов"""
        if len(number_history) < 10:
            return np.zeros(15, dtype=np.float32)
        
        ts = np.array(number_history)
        features = []
        
        # 1. Анализ временных рядов
        ts_features = self._analyze_time_series(ts)
        features.extend([
            ts_features.get('linear_trend', 0),
            ts_features.get('volatility', 0),
            ts_features.get('hurst_exponent', 0.5),
            ts_features.get('mean_reversion', 0),
        ])
        
        # Автокорреляции
        autocorr = ts_features.get('autocorrelation', {})
        features.extend([
            autocorr.get('autocorr_lag_1', 0),
            autocorr.get('autocorr_lag_2', 0), 
            autocorr.get('autocorr_lag_3', 0),
        ])
        
        # 2. Статистические моменты
        if len(ts) > 1:
            features.extend([
                stats.skew(ts) if len(ts) > 2 else 0,
                stats.kurtosis(ts) if len(ts) > 3 else 0,
            ])
        else:
            features.extend([0.0, 0.0])
        
        # 3. Паттерны последовательностей
        pattern_features = self._analyze_sequences(ts)
        features.extend([
            pattern_features.get('sequence_count', 0) / len(ts),
            pattern_features.get('avg_sequence_length', 0),
            pattern_features.get('max_sequence_length', 0) / 10.0,
        ])
        
        # 4. Распределение чисел
        dist_features = self._analyze_distribution(ts)
        features.extend([
            dist_features.get('entropy', 0),
            dist_features.get('hot_numbers_ratio', 0),
            dist_features.get('cold_numbers_ratio', 0),
        ])
        
        return np.array(features, dtype=np.float32)
    
    def _analyze_time_series(self, ts: np.ndarray) -> Dict[str, float]:
        """Анализ временных рядов"""
        result = {}
        
        # Автокорреляция
        autocorr = {}
        for lag in [1, 2, 3]:
            if len(ts) > lag:
                try:
                    corr = np.corrcoef(ts[:-lag], ts[lag:])[0,1]
                    if not np.isnan(corr):
                        autocorr[f"autocorr_lag_{lag}"] = corr
                except:
                    autocorr[f"autocorr_lag_{lag}"] = 0.0
        
        # Тренды
        x = np.arange(len(ts))
        try:
            linear_trend = stats.linregress(x, ts).slope if len(ts) > 1 else 0
        except:
            linear_trend = 0
        
        result.update({
            'autocorrelation': autocorr,
            'linear_trend': linear_trend,
            'volatility': np.std(ts) if len(ts) > 1 else 0,
            'hurst_exponent': self._calculate_hurst_safe(ts),
            'mean_reversion': self._check_mean_reversion(ts),
        })
        
        return result
    
    def _analyze_sequences(self, ts: np.ndarray) -> Dict[str, float]:
        """Анализ последовательностей"""
        sequences = []
        current_seq = [ts[0]]
        
        for i in range(1, len(ts)):
            if abs(ts[i] - ts[i-1]) <= 2:
                current_seq.append(ts[i])
            else:
                if len(current_seq) >= 2:
                    sequences.append(current_seq)
                current_seq = [ts[i]]
        
        if len(current_seq) >= 2:
            sequences.append(current_seq)
        
        sequence_lengths = [len(seq) for seq in sequences]
        
        return {
            'sequence_count': len(sequences),
            'avg_sequence_length': np.mean(sequence_lengths) if sequence_lengths else 0,
            'max_sequence_length': max(sequence_lengths) if sequence_lengths else 0,
        }
    
    def _analyze_distribution(self, ts: np.ndarray) -> Dict[str, float]:
        """Анализ распределения чисел"""
        freq = {}
        for num in ts:
            freq[int(num)] = freq.get(int(num), 0) + 1
        
        # Энтропия
        total = len(ts)
        probabilities = [count/total for count in freq.values()]
        entropy = -sum(p * np.log(p + 1e-8) for p in probabilities)
        
        # "Горячие" и "холодные" числа
        avg_freq = total / 26
        hot_numbers = [num for num, count in freq.items() if count > avg_freq * 1.5]
        cold_numbers = [num for num in range(1, 27) if num not in freq or freq.get(num, 0) < avg_freq * 0.5]
        
        return {
            'entropy': entropy,
            'hot_numbers_ratio': len(hot_numbers) / 26,
            'cold_numbers_ratio': len(cold_numbers) / 26,
        }
    
    def _calculate_hurst_safe(self, ts: np.ndarray) -> float:
        """Безопасный расчет Hurst exponent"""
        if len(ts) < 20:
            return 0.5
        
        try:
            n = len(ts)
            mean_val = np.mean(ts)
            deviations = ts - mean_val
            cumulative_deviations = np.cumsum(deviations)
            
            data_range = np.max(cumulative_deviations) - np.min(cumulative_deviations)
            std_dev = np.std(ts)
            
            if std_dev == 0:
                return 0.5
                
            rs_statistic = data_range / std_dev
            
            if rs_statistic <= 0:
                return 0.5
                
            hurst = np.log(rs_statistic) / np.log(n)
            return float(np.clip(hurst, 0.1, 0.9))
            
        except Exception:
            return 0.5
    
    def _check_mean_reversion(self, ts: np.ndarray) -> float:
        """Проверка mean reversion"""
        if len(ts) < 10:
            return 0.0
        
        mean = np.mean(ts)
        deviations = np.abs(ts - mean)
        return float(np.mean(deviations) / (np.std(ts) + 1e-8))
    
    def get_feature_names(self) -> List[str]:
        """Получение имен features"""
        return self._feature_names
    
    def _generate_feature_names(self) -> List[str]:
        """Генерация имен features"""
        return [
            'linear_trend', 'volatility', 'hurst_exponent', 'mean_reversion',
            'autocorr_lag_1', 'autocorr_lag_2', 'autocorr_lag_3',
            'skewness', 'kurtosis',
            'sequence_ratio', 'avg_sequence_length', 'max_sequence_ratio',
            'entropy', 'hot_numbers_ratio', 'cold_numbers_ratio'
        ]
