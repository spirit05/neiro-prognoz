# [file name]: model/advanced_features.py
"""
Продвинутые features для анализа временных рядов
"""

import numpy as np
from scipy import stats
from typing import List, Dict
import torch

class AdvancedPatternAnalyzer:
    def __init__(self):
        self.patterns = {}
    
    def analyze_time_series(self, history: List[int]) -> Dict:
        """Глубокий анализ временных рядов"""
        if len(history) < 10:
            return {}
        
        ts = np.array(history)
        
        # Автокорреляция на разных лагах
        autocorr = {}
        for lag in [1, 2, 3, 5, 7]:
            if len(ts) > lag:
                try:
                    corr = np.corrcoef(ts[:-lag], ts[lag:])[0,1]
                    if not np.isnan(corr):
                        autocorr[f"autocorr_lag_{lag}"] = corr
                except:
                    autocorr[f"autocorr_lag_{lag}"] = 0.0
        
        # Сезонность (периодичность)
        try:
            fft = np.fft.fft(ts)
            frequencies = np.fft.fftfreq(len(ts))
            dominant_idx = np.argmax(np.abs(fft[1:])) + 1
            dominant_freq = frequencies[dominant_idx] if dominant_idx < len(frequencies) else 0
        except:
            dominant_freq = 0
        
        # Тренды
        x = np.arange(len(ts))
        try:
            linear_trend = stats.linregress(x, ts).slope if len(ts) > 1 else 0
        except:
            linear_trend = 0
        
        return {
            'autocorrelation': autocorr,
            'dominant_frequency': dominant_freq,
            'linear_trend': linear_trend,
            'volatility': np.std(ts) if len(ts) > 1 else 0,
            'hurst_exponent': self._calculate_hurst(ts),
            'mean_reversion': self._check_mean_reversion(ts)
        }
    
    def _calculate_hurst(self, ts: np.ndarray) -> float:
        """Вычисление экспоненты Херста для определения персистентности"""
        if len(ts) < 20:
            return 0.5
        
        try:
            lags = range(2, min(20, len(ts)//2))
            tau = [np.std(np.subtract(ts[lag:], ts[:-lag])) for lag in lags]
            if len(tau) < 2:
                return 0.5
            poly = np.polyfit(np.log(lags), np.log(tau), 1)
            return poly[0]
        except:
            return 0.5
    
    def _check_mean_reversion(self, ts: np.ndarray) -> float:
        """Проверка mean reversion (возвращения к среднему)"""
        if len(ts) < 10:
            return 0.0
        
        mean = np.mean(ts)
        deviations = np.abs(ts - mean)
        return float(np.mean(deviations) / (np.std(ts) + 1e-8))

class FrequencyBasedPredictor:
    def __init__(self):
        self.number_frequencies = {}
        self.pair_frequencies = {}
        self.position_frequencies = {0: {}, 1: {}, 2: {}, 3: {}}
        self.total_groups = 0
    
    def update_frequencies(self, dataset: List[str]):
        """Обновление частотных характеристик"""
        # Сбрасываем частоты
        self.position_frequencies = {0: {}, 1: {}, 2: {}, 3: {}}
        self.pair_frequencies = {}
        self.number_frequencies = {}
        
        all_numbers = []
        self.total_groups = len(dataset)
        
        for group_str in dataset:
            try:
                numbers = [int(x) for x in group_str.strip().split()]
                if len(numbers) != 4:
                    continue
                    
                all_numbers.extend(numbers)
                
                # Частоты чисел по позициям
                for i, num in enumerate(numbers):
                    self.position_frequencies[i][num] = self.position_frequencies[i].get(num, 0) + 1
                
                # Частоты пар
                pair1 = tuple(sorted(numbers[:2]))
                pair2 = tuple(sorted(numbers[2:]))
                self.pair_frequencies[pair1] = self.pair_frequencies.get(pair1, 0) + 1
                self.pair_frequencies[pair2] = self.pair_frequencies.get(pair2, 0) + 1
            except:
                continue
        
        # Общие частоты чисел
        for num in all_numbers:
            self.number_frequencies[num] = self.number_frequencies.get(num, 0) + 1
    
    def get_probability_scores(self, group: tuple) -> float:
        """Вычисление вероятностного score для группы"""
        if self.total_groups == 0:
            return 0.001  # Базовый score при отсутствии данных
        
        score = 1.0
        
        # Вероятности по позициям
        for i, num in enumerate(group):
            pos_freq = self.position_frequencies[i].get(num, 0)
            # Additive smoothing (Laplace)
            score *= (pos_freq + 1) / (self.total_groups + 26)
        
        # Вероятности пар
        pair1 = tuple(sorted(group[:2]))
        pair2 = tuple(sorted(group[2:]))
        
        total_pairs = self.total_groups
        pair1_prob = (self.pair_frequencies.get(pair1, 0) + 1) / (total_pairs + 325)  # 26*25/2 = 325
        pair2_prob = (self.pair_frequencies.get(pair2, 0) + 1) / (total_pairs + 325)
        
        score *= pair1_prob * pair2_prob
        
        # Нормализация и логарифмирование для стабильности
        return max(1e-10, score)

class SmartNumberSelector:
    def __init__(self, memory_size: int = 50):
        self.memory_size = memory_size
        self.history = []
    
    def analyze_temperature(self, dataset: List[str]) -> Dict[str, List[int]]:
        """Анализ 'температуры' чисел с учетом временного горизонта"""
        if not dataset:
            return {'hot': [], 'cold': [], 'neutral': list(range(1, 27))}
        
        recent_data = dataset[-self.memory_size:] if len(dataset) > self.memory_size else dataset
        all_time_data = dataset
        
        recent_numbers = self._extract_numbers(recent_data)
        all_time_numbers = self._extract_numbers(all_time_data)
        
        if not recent_numbers or not all_time_numbers:
            return {'hot': [], 'cold': [], 'neutral': list(range(1, 27))}
        
        hot_numbers = []
        cold_numbers = []
        
        for num in range(1, 27):
            recent_freq = recent_numbers.count(num) / len(recent_numbers)
            all_time_freq = all_time_numbers.count(num) / len(all_time_numbers)
            
            if all_time_freq == 0:
                continue
                
            ratio = recent_freq / all_time_freq
            
            # Число считается "горячим" если его частота в последнее время выше средней
            if ratio > 1.5:
                hot_numbers.append(num)
            elif ratio < 0.5:
                cold_numbers.append(num)
        
        neutral = [n for n in range(1, 27) if n not in hot_numbers and n not in cold_numbers]
        
        return {
            'hot': hot_numbers,
            'cold': cold_numbers,
            'neutral': neutral
        }
    
    def _extract_numbers(self, dataset: List[str]) -> List[int]:
        """Извлечение всех чисел из датасета"""
        numbers = []
        for group_str in dataset:
            try:
                numbers.extend([int(x) for x in group_str.strip().split()])
            except:
                continue
        return numbers