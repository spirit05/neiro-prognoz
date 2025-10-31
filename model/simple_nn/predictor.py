# model/simple_nn/predictor.py
"""
УСИЛЕННОЕ предсказание групп чисел
"""

import torch
import numpy as np
from typing import List, Tuple
import os
from .model import EnhancedNumberPredictor
from .features import FeatureExtractor

class EnhancedPredictor:
    def __init__(self, model_path: str = "data/simple_model.pth"):
        self.model_path = model_path
        self.device = torch.device('cpu')
        self.model = None
        self.feature_extractor = FeatureExtractor(history_size=25)  # Увеличили историю
        self.is_trained = False
        
    def load_model(self) -> bool:
        """Загрузка обученной модели"""
        if not os.path.exists(self.model_path):
            print(f"❌ Файл модели не найден: {self.model_path}")
            return False
            
        try:
            checkpoint = torch.load(self.model_path, map_location='cpu')
            config = checkpoint['model_config']
            self.model = EnhancedNumberPredictor(
                input_size=config['input_size'],
                hidden_size=config['hidden_size']
            )
            self.model.load_state_dict(checkpoint['model_state_dict'])
            self.model.to(self.device)
            self.model.eval()
            
            self.is_trained = True
            print(f"✅ УСИЛЕННАЯ нейросеть загружена: {self.model_path}")
            return True
            
        except Exception as e:
            print(f"❌ Ошибка загрузки модели: {e}")
            return False
    
    def predict_group(self, number_history: List[int], top_k: int = 10) -> List[Tuple[Tuple[int, int, int, int], float]]:
        """УСИЛЕННОЕ предсказание следующей группы чисел"""
        if not self.is_trained or self.model is None:
            if not self.load_model():
                return []
        
        if len(number_history) < 25:  # Увеличили минимальную историю
            print("❌ Недостаточно данных в истории")
            return []
        
        features = self.feature_extractor.extract_features(number_history)
        features_tensor = torch.tensor(features, dtype=torch.float32).unsqueeze(0)
        
        with torch.no_grad():
            outputs = self.model(features_tensor)
            probabilities = torch.softmax(outputs, dim=-1)
            
            # Усиленная генерация кандидатов
            candidates = self._generate_enhanced_candidates(probabilities[0], top_k, number_history)
            return candidates
    
    def _generate_enhanced_candidates(self, probabilities: torch.Tensor, top_k: int, history: List[int]) -> List[Tuple[Tuple[int, int, int, int], float]]:
        """УСИЛЕННАЯ генерация кандидатных групп"""
        candidates = []
        
        # Глубокий анализ истории
        pattern_analysis = self._deep_pattern_analysis(history)
        
        # Генерация на основе модели
        model_candidates = self._generate_model_based_candidates(probabilities, 20, pattern_analysis)
        candidates.extend(model_candidates)
        
        # Генерация на основе паттернов
        pattern_candidates = self._generate_intelligent_patterns(history, 15, pattern_analysis)
        candidates.extend(pattern_candidates)
        
        # Сортировка и фильтрация
        candidates.sort(key=lambda x: x[1], reverse=True)
        
        # Убираем дубликаты
        unique_candidates = []
        seen = set()
        for group, score in candidates:
            if group not in seen:
                seen.add(group)
                unique_candidates.append((group, score))
            if len(unique_candidates) >= top_k * 2:  # Берем в 2 раза больше для фильтрации
                break
        
        # Фильтрация по качеству
        filtered_candidates = self._filter_candidates_by_quality(unique_candidates, pattern_analysis)
        
        return filtered_candidates[:top_k]
    
    def _deep_pattern_analysis(self, history: List[int]) -> dict:
        """Глубокий анализ паттернов в истории"""
        if len(history) < 10:
            return {}
            
        recent = history[-20:]
        
        # Анализ частот
        freq = {}
        for num in recent:
            freq[num] = freq.get(num, 0) + 1
        
        # "Горячие" и "холодные" числа
        avg_freq = len(recent) / 26
        hot_numbers = [num for num, count in freq.items() if count > avg_freq * 1.5]
        cold_numbers = [num for num in range(1, 27) if num not in freq or freq[num] < avg_freq * 0.5]
        
        # Анализ последовательностей
        sequences = []
        current_seq = [recent[0]]
        for i in range(1, len(recent)):
            if recent[i] == recent[i-1] + 1 or recent[i] == recent[i-1] - 1:
                current_seq.append(recent[i])
            else:
                if len(current_seq) >= 3:
                    sequences.append(current_seq)
                current_seq = [recent[i]]
        
        return {
            'hot_numbers': hot_numbers,
            'cold_numbers': cold_numbers,
            'sequences': sequences,
            'frequencies': freq,
            'recent_numbers': recent
        }
    
    def _generate_model_based_candidates(self, probabilities: torch.Tensor, count: int, pattern_analysis: dict) -> List[Tuple[Tuple[int, int, int, int], float]]:
        """Генерация кандидатов на основе модели с учетом паттернов"""
        candidates = []
        
        # Берем топ-7 чисел для каждой позиции
        top_numbers = []
        for pos in range(4):
            probs = probabilities[pos]
            top_probs, top_indices = torch.topk(probs, 7)
            top_numbers.append([
                (idx.item() + 1, prob.item()) for idx, prob in zip(top_indices, top_probs)
            ])
        
        # Генерируем комбинации с приоритетом для "холодных" чисел
        cold_bonus = 1.5
        hot_penalty = 0.8
        
        for i, (n1, p1) in enumerate(top_numbers[0]):
            for j, (n2, p2) in enumerate(top_numbers[1]):
                if n1 == n2:
                    continue
                for k, (n3, p3) in enumerate(top_numbers[2]):
                    if n3 in [n1, n2]:
                        continue
                    for l, (n4, p4) in enumerate(top_numbers[3]):
                        if n4 in [n1, n2, n3]:
                            continue
                        
                        group = (n1, n2, n3, n4)
                        
                        # Корректируем score на основе паттернов
                        base_score = p1 * p2 * p3 * p4
                        
                        # Бонусы/штрафы
                        pattern_score = self._calculate_enhanced_pattern_score(group, pattern_analysis)
                        adjusted_score = base_score * pattern_score
                        
                        # Усиливаем хорошие предсказания
                        if adjusted_score > 0.0001:
                            adjusted_score *= 2
                        
                        candidates.append((group, adjusted_score))
                        
                        if len(candidates) >= count * 10:  # Ограничиваем количество
                            return candidates
        
        return candidates
    
    def _calculate_enhanced_pattern_score(self, group: Tuple[int, int, int, int], pattern_analysis: dict) -> float:
        """Расчет усиленного pattern score"""
        score = 1.0
        hot_numbers = pattern_analysis.get('hot_numbers', [])
        cold_numbers = pattern_analysis.get('cold_numbers', [])
        
        # Бонус за холодные числа
        cold_count = sum(1 for num in group if num in cold_numbers)
        score *= (1 + cold_count * 0.3)
        
        # Штраф за слишком много горячих чисел
        hot_count = sum(1 for num in group if num in hot_numbers)
        if hot_count >= 3:
            score *= 0.7
        
        # Бонус за сбалансированность
        even_count = sum(1 for num in group if num % 2 == 0)
        if even_count == 2:
            score *= 1.2
        
        # Бонус за разнообразие диапазонов
        low_count = sum(1 for num in group if num <= 13)
        high_count = sum(1 for num in group if num > 13)
        if low_count == 2 and high_count == 2:
            score *= 1.3
        
        # Бонус за уникальность всех чисел
        if len(set(group)) == 4:
            score *= 1.2
        
        return score
    
    def _generate_intelligent_patterns(self, history: List[int], count: int, pattern_analysis: dict) -> List[Tuple[Tuple[int, int, int, int], float]]:
        """Генерация интеллектуальных паттернов"""
        candidates = []
        import random
        
        hot_numbers = pattern_analysis.get('hot_numbers', [])
        cold_numbers = pattern_analysis.get('cold_numbers', [])
        
        strategies = [
            lambda: self._strategy_mixed_hot_cold(hot_numbers, cold_numbers),
            lambda: self._strategy_balanced_ranges(),
            lambda: self._strategy_follow_sequences(pattern_analysis.get('sequences', [])),
            lambda: self._strategy_avoid_recent(pattern_analysis.get('recent_numbers', [])),
        ]
        
        for _ in range(count):
            strategy = random.choice(strategies)
            group = strategy()
            
            if group and group not in [c[0] for c in candidates]:
                # Высокий базовый score для паттернных кандидатов
                candidates.append((group, 0.001))
        
        return candidates
    
    def _strategy_mixed_hot_cold(self, hot_numbers: List[int], cold_numbers: List[int]) -> Tuple[int, int, int, int]:
        """Стратегия: смесь горячих и холодных чисел"""
        import random
        
        if not cold_numbers:
            cold_numbers = list(range(1, 27))
        if not hot_numbers:
            hot_numbers = list(range(1, 27))
        
        # 2 холодных + 2 горячих
        cold_choices = random.sample(cold_numbers, min(2, len(cold_numbers)))
        hot_choices = random.sample(hot_numbers, min(2, len(hot_numbers)))
        
        return self._create_valid_group(cold_choices + hot_choices)
    
    def _strategy_balanced_ranges(self) -> Tuple[int, int, int, int]:
        """Стратегия: сбалансированные диапазоны"""
        import random
        
        low_pool = list(range(1, 14))
        high_pool = list(range(14, 27))
        
        low_choices = random.sample(low_pool, 2)
        high_choices = random.sample(high_pool, 2)
        
        return self._create_valid_group(low_choices + high_choices)
    
    def _strategy_follow_sequences(self, sequences: List[List[int]]) -> Tuple[int, int, int, int]:
        """Стратегия: следование последовательностям"""
        import random
        
        if sequences:
            # Берем последнюю последовательность
            last_seq = sequences[-1]
            if len(last_seq) >= 2:
                # Продолжаем последовательность
                base_num = last_seq[-1]
                next_nums = [base_num + 1, base_num - 1]
                valid_nums = [n for n in next_nums if 1 <= n <= 26]
                
                if valid_nums:
                    base_choices = [base_num] + valid_nums[:1]
                    remaining = [n for n in range(1, 27) if n not in base_choices]
                    other_choices = random.sample(remaining, 2)
                    return self._create_valid_group(base_choices + other_choices)
        
        return self._strategy_balanced_ranges()
    
    def _strategy_avoid_recent(self, recent: List[int]) -> Tuple[int, int, int, int]:
        """Стратегия: избегание недавних чисел"""
        import random
        
        avoid_set = set(recent[-8:])  # Избегаем последние 8 чисел
        available = [n for n in range(1, 27) if n not in avoid_set]
        
        if len(available) >= 4:
            choices = random.sample(available, 4)
            return self._create_valid_group(choices)
        else:
            return self._strategy_balanced_ranges()
    
    def _create_valid_group(self, numbers: List[int]) -> Tuple[int, int, int, int]:
        """Создание валидной группы из чисел"""
        import random
        
        if len(numbers) < 4:
            # Добираем числа
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
    
    def _filter_candidates_by_quality(self, candidates: List[tuple], pattern_analysis: dict) -> List[tuple]:
        """Фильтрация кандидатов по качеству"""
        filtered = []
        
        for group, score in candidates:
            # Базовая проверка качества
            quality_score = self._calculate_quality_score(group, pattern_analysis)
            final_score = score * quality_score
            
            if final_score > 0.00005:  # Более высокий порог
                filtered.append((group, final_score))
        
        # Сортируем по убыванию score
        filtered.sort(key=lambda x: x[1], reverse=True)
        return filtered
    
    def _calculate_quality_score(self, group: Tuple[int, int, int, int], pattern_analysis: dict) -> float:
        """Расчет score качества группы"""
        score = 1.0
        
        # Проверка уникальности
        if len(set(group)) < 4:
            score *= 0.5
        
        # Проверка сбалансированности
        even_count = sum(1 for num in group if num % 2 == 0)
        if even_count == 0 or even_count == 4:
            score *= 0.7
        
        # Проверка диапазонов
        low_count = sum(1 for num in group if num <= 13)
        if low_count == 0 or low_count == 4:
            score *= 0.8
        
        return score