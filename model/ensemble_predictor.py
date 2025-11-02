# [file name]: model/ensemble_predictor.py (ИСПРАВЛЕННЫЙ)
"""
Ансамблевые предсказания с комбинированием моделей
"""

import numpy as np
from typing import List, Tuple, Dict
import sys
import os

# Добавляем путь для импорта
current_dir = os.path.dirname(os.path.abspath(__file__))
if current_dir not in sys.path:
    sys.path.insert(0, current_dir)

class StatisticalPredictor:
    """Статистический предсказатель на основе паттернов"""
    
    def __init__(self):
        self._pattern_analyzer = None
    
    def _get_pattern_analyzer(self):
        """Ленивая загрузка анализатора паттернов"""
        if self._pattern_analyzer is None:
            try:
                from model.advanced_features import AdvancedPatternAnalyzer
                self._pattern_analyzer = AdvancedPatternAnalyzer()
            except ImportError as e:
                print(f"⚠️  Не удалось загрузить анализатор паттернов: {e}")
                self._pattern_analyzer = None
        return self._pattern_analyzer
    
    def predict(self, history: List[int], top_k: int = 10) -> List[Tuple[Tuple[int, int, int, int], float]]:
        """Статистическое предсказание на основе паттернов"""
        if len(history) < 20:
            return []
        
        analyzer = self._get_pattern_analyzer()
        patterns = analyzer.analyze_time_series(history) if analyzer else {}
        
        # Генерация кандидатов на основе статистических паттернов
        candidates = self._generate_statistical_candidates(history, patterns, top_k * 2)
        return candidates[:top_k]
    
    def _generate_statistical_candidates(self, history: List[int], patterns: Dict, count: int) -> List[tuple]:
        """Генерация кандидатов на основе статистических паттернов"""
        import random
        
        candidates = []
        recent = history[-10:] if len(history) >= 10 else history
        
        # Анализ автокорреляции
        autocorr = patterns.get('autocorrelation', {})
        trending = patterns.get('linear_trend', 0)
        
        for _ in range(count):
            # Стратегия: продолжение тренда
            if abs(trending) > 0.1:
                base_nums = random.sample(recent, min(2, len(recent)))
                new_nums = [max(1, min(26, int(x + trending * random.uniform(1, 3)))) for x in base_nums]
                group = self._create_valid_group(new_nums + [random.randint(1, 26) for _ in range(2)])
            # Стратегия: mean reversion
            elif patterns.get('mean_reversion', 0) > 1.0:
                mean_val = np.mean(history)
                group = self._create_valid_group([
                    max(1, min(26, int(mean_val + random.uniform(-3, 3)))) for _ in range(4)
                ])
            # Случайная стратегия с учетом автокорреляции
            else:
                group = self._create_valid_group([random.randint(1, 26) for _ in range(4)])
            
            if group:
                # Базовый score для статистических кандидатов
                score = 0.001 * (1 + len(autocorr) * 0.1)
                candidates.append((group, score))
        
        return candidates
    
    def _create_valid_group(self, numbers: List[int]) -> Tuple[int, int, int, int]:
        """Создание валидной группы из чисел"""
        import random
        
        if len(numbers) < 4:
            all_nums = list(range(1, 27))
            additional = [n for n in all_nums if n not in numbers]
            numbers.extend(random.sample(additional, 4 - len(numbers)))
        
        # Создаем валидные пары
        first_pair = numbers[:2]
        second_pair = numbers[2:4]
        
        # Проверяем уникальность в парах
        if first_pair[0] == first_pair[1]:
            first_pair[1] = random.choice([n for n in range(1, 27) if n != first_pair[0]])
        if second_pair[0] == second_pair[1]:
            second_pair[1] = random.choice([n for n in range(1, 27) if n != second_pair[0]])
        
        return (first_pair[0], first_pair[1], second_pair[0], second_pair[1])

# ... остальной код ensemble_predictor.py без изменений ...

class PatternBasedPredictor:
    """Предсказатель на основе паттернов последовательностей"""
    
    def predict(self, history: List[int], top_k: int = 10) -> List[Tuple[Tuple[int, int, int, int], float]]:
        """Предсказание на основе паттернов последовательностей"""
        if len(history) < 15:
            return []
        
        candidates = []
        
        # Анализ последовательностей
        sequences = self._find_sequences(history)
        
        for seq in sequences[-3:]:  # Берем последние 3 последовательности
            if len(seq) >= 3:
                # Продолжаем последовательность
                last_num = seq[-1]
                possible_next = [last_num + 1, last_num - 1, last_num + 2, last_num - 2]
                valid_next = [n for n in possible_next if 1 <= n <= 26]
                
                if valid_next:
                    base_group = [last_num] + valid_next[:1]
                    group = self._complete_group(base_group)
                    if group:
                        candidates.append((group, 0.002))
        
        return candidates[:top_k]
    
    def _find_sequences(self, history: List[int]) -> List[List[int]]:
        """Поиск последовательностей в истории"""
        sequences = []
        current_seq = [history[0]]
        
        for i in range(1, len(history)):
            if abs(history[i] - history[i-1]) <= 2:  # Последовательности с шагом <= 2
                current_seq.append(history[i])
            else:
                if len(current_seq) >= 3:
                    sequences.append(current_seq)
                current_seq = [history[i]]
        
        if len(current_seq) >= 3:
            sequences.append(current_seq)
        
        return sequences
    
    def _complete_group(self, base_numbers: List[int]) -> Tuple[int, int, int, int]:
        """Дополнение группы до 4 чисел"""
        import random
        
        if len(base_numbers) >= 4:
            return self._create_valid_group(base_numbers[:4])
        
        all_nums = list(range(1, 27))
        available = [n for n in all_nums if n not in base_numbers]
        
        if len(available) < (4 - len(base_numbers)):
            return None
        
        additional = random.sample(available, 4 - len(base_numbers))
        return self._create_valid_group(base_numbers + additional)
    
    def _create_valid_group(self, numbers: List[int]) -> Tuple[int, int, int, int]:
        """Создание валидной группы"""
        import random
        
        if len(numbers) < 4:
            return None
            
        first_pair = numbers[:2]
        second_pair = numbers[2:4]
        
        if first_pair[0] == first_pair[1]:
            first_pair[1] = random.choice([n for n in range(1, 27) if n != first_pair[0]])
        if second_pair[0] == second_pair[1]:
            second_pair[1] = random.choice([n for n in range(1, 27) if n != second_pair[0]])
        
        return (first_pair[0], first_pair[1], second_pair[0], second_pair[1])

class EnsemblePredictor:
    def __init__(self):
        self.predictors = {
            'frequency': None,
            'pattern': None, 
            'statistical': None,
            'neural': None
        }
        # Веса моделей (будут адаптироваться)
        # self.weights = {
        #     'frequency': 0.35,
        #     'pattern': 0.25,
        #     'statistical': 0.20,
        #     'neural': 0.20
        # }
        self.weights = {'neural': 1.0}  # ⚡ ТОЛЬКО НЕЙРОСЕТЬ
        
        self._number_selector = None
        self.dataset = []
    
    def _get_frequency_predictor(self):
        """Ленивая загрузка частотного предсказателя"""
        if self.predictors['frequency'] is None:
            try:
                from model.advanced_features import FrequencyBasedPredictor
                self.predictors['frequency'] = FrequencyBasedPredictor()
            except ImportError as e:
                print(f"⚠️  Не удалось загрузить частотный предсказатель: {e}")
        return self.predictors['frequency']
    
    def _get_pattern_predictor(self):
        """Ленивая загрузка паттернного предсказателя"""
        if self.predictors['pattern'] is None:
            try:
                self.predictors['pattern'] = PatternBasedPredictor()
            except Exception as e:
                print(f"⚠️  Не удалось загрузить паттернный предсказатель: {e}")
        return self.predictors['pattern']
    
    def _get_statistical_predictor(self):
        """Ленивая загрузка статистического предсказателя"""
        if self.predictors['statistical'] is None:
            try:
                self.predictors['statistical'] = StatisticalPredictor()
            except Exception as e:
                print(f"⚠️  Не удалось загрузить статистический предсказатель: {e}")
        return self.predictors['statistical']
    
    def _get_number_selector(self):
        """Ленивая загрузка селектора чисел"""
        if self._number_selector is None:
            try:
                from model.advanced_features import SmartNumberSelector
                self._number_selector = SmartNumberSelector()
            except ImportError as e:
                print(f"⚠️  Не удалось загрузить селектор чисел: {e}")
                self._number_selector = None
        return self._number_selector
    
    def set_neural_predictor(self, neural_predictor):
        """Установка нейросетевого предсказателя"""
        self.predictors['neural'] = neural_predictor
    
    def update_ensemble(self, dataset: List[str]):
        """Обновление ансамбля с новыми данными"""
        self.dataset = dataset
        
        # Обновляем частотный предсказатель
        freq_predictor = self._get_frequency_predictor()
        if freq_predictor:
            freq_predictor.update_frequencies(dataset)
    
    def predict_ensemble(self, history: List[int], top_k: int = 15) -> List[Tuple[Tuple[int, int, int, int], float]]:
        """Ансамблевое предсказание"""
        all_predictions = []
        
        # Анализ температуры чисел
        temperature = {}
        selector = self._get_number_selector()
        if selector:
            temperature = selector.analyze_temperature(self.dataset)
        
        # Получаем предсказания от всех моделей
        for name in ['frequency', 'pattern', 'statistical', 'neural']:
            predictor = None
            
            if name == 'frequency':
                predictor = self._get_frequency_predictor()
            elif name == 'pattern':
                predictor = self._get_pattern_predictor()
            elif name == 'statistical':
                predictor = self._get_statistical_predictor()
            elif name == 'neural':
                predictor = self.predictors['neural']
            
            if predictor is None:
                continue
                
            try:
                if hasattr(predictor, 'predict_group'):  # Нейросетевой предсказатель
                    predictions = predictor.predict_group(history, top_k * 2)
                elif hasattr(predictor, 'predict'):  # Другие предсказатели
                    predictions = predictor.predict(history, top_k * 2)
                else:
                    continue
                
                # Взвешиваем score
                weight = self.weights[name]
                weighted_predictions = [(group, score * weight) for group, score in predictions]
                all_predictions.extend(weighted_predictions)
                
            except Exception as e:
                print(f"❌ Ошибка в предсказателе {name}: {e}")
                continue
        
        # Объединяем и агрегируем score
        combined = {}
        for group, score in all_predictions:
            combined[group] = combined.get(group, 0) + score
        
        # Применяем температурные корректировки
        final_predictions = []
        for group, score in combined.items():
            adjusted_score = self._apply_temperature_adjustment(group, score, temperature)
            final_predictions.append((group, adjusted_score))
        
        # Сортируем по убыванию score
        final_predictions.sort(key=lambda x: x[1], reverse=True)
        
        return final_predictions[:top_k]
    
    def _apply_temperature_adjustment(self, group: tuple, score: float, temperature: Dict) -> float:
        """Корректировка score на основе температуры чисел"""
        adjusted_score = score
        
        hot_numbers = temperature.get('hot', [])
        cold_numbers = temperature.get('cold', [])
        
        # Бонус за холодные числа
        cold_count = sum(1 for num in group if num in cold_numbers)
        if cold_count > 0:
            adjusted_score *= (1 + cold_count * 0.4)
        
        # Штраф за слишком много горячих чисел
        hot_count = sum(1 for num in group if num in hot_numbers)
        if hot_count >= 3:
            adjusted_score *= 0.6
        
        # Бонус за сбалансированность
        unique_count = len(set(group))
        if unique_count == 4:
            adjusted_score *= 1.3
        
        return adjusted_score
    
    def adjust_weights_based_performance(self, actual_groups: List[tuple]):
        """Адаптация весов на основе производительности"""
        # Простая стратегия: увеличиваем вес моделей, которые лучше предсказывали
        # В реальной системе здесь была бы более сложная логика
        pass
