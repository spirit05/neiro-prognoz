# [file name]: model/ensemble_predictor.py
"""
Ансамблевые предсказания с комбинированием моделей
"""

import numpy as np
from typing import List, Tuple, Dict
from .advanced_features import FrequencyBasedPredictor, AdvancedPatternAnalyzer, SmartNumberSelector
from .simple_nn.predictor import EnhancedPredictor
from .data_loader import load_dataset

class StatisticalPredictor:
    """Статистический предсказатель на основе паттернов"""
    
    def __init__(self):
        self.pattern_analyzer = AdvancedPatternAnalyzer()
    
    def predict(self, history: List[int], top_k: int = 10) -> List[Tuple[Tuple[int, int, int, int], float]]:
        """Статистическое предсказание на основе паттернов"""
        if len(history) < 20:
            return []
        
        patterns = self.pattern_analyzer.analyze_time_series(history)
        
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
            'frequency': FrequencyBasedPredictor(),
            'pattern': PatternBasedPredictor(), 
            'statistical': StatisticalPredictor(),
            'neural': None  # Будет установлен позже
        }
        # Веса моделей (будут адаптироваться)
        self.weights = {
            'frequency': 0.35,
            'pattern': 0.25,
            'statistical': 0.20,
            'neural': 0.20
        }
        
        self.number_selector = SmartNumberSelector()
        self.dataset = []
    
    def set_neural_predictor(self, neural_predictor):
        """Установка нейросетевого предсказателя"""
        self.predictors['neural'] = neural_predictor
    
    def update_ensemble(self, dataset: List[str]):
        """Обновление ансамбля с новыми данными"""
        self.dataset = dataset
        self.predictors['frequency'].update_frequencies(dataset)
    
    def predict_ensemble(self, history: List[int], top_k: int = 15) -> List[Tuple[Tuple[int, int, int, int], float]]:
        """Ансамблевое предсказание"""
        all_predictions = []
        
        # Анализ температуры чисел
        temperature = self.number_selector.analyze_temperature(self.dataset)
        
        # Получаем предсказания от всех моделей
        for name, predictor in self.predictors.items():
            if predictor is None:
                continue
                
            try:
                if name == 'neural':
                    predictions = predictor.predict_group(history, top_k * 2) if hasattr(predictor, 'predict_group') else []
                else:
                    predictions = predictor.predict(history, top_k * 2)
                
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