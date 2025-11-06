"""
УСИЛЕННОЕ предсказание групп чисел с ансамблевыми методами - МОДУЛЬНАЯ АРХИТЕКТУРА
"""

import torch
import numpy as np
from typing import List, Tuple
import os
from config import paths, logging_config, constants

logger = logging_config.get_ml_system_logger()

class EnhancedPredictor:
    def __init__(self, model_path: str = None):
        self.model_path = model_path or paths.MODEL_FILE
        self.device = torch.device('cpu')
        self.model = None
        self._feature_extractor = None
        self.is_trained = False
        
        # Ленивая загрузка ансамблевой системы
        self._ensemble_predictor = None
        self._pattern_analyzer = None
        self.use_ensemble = True
    
    def _get_feature_extractor(self):
        """Ленивая загрузка FeatureExtractor"""
        if self._feature_extractor is None:
            try:
                from ml.features.extractor import FeatureExtractor
                self._feature_extractor = FeatureExtractor(history_size=25)
            except ImportError as e:
                logger.error(f"❌ Не удалось загрузить FeatureExtractor: {e}")
                # Fallback на базовый экстрактор
                from ml.features.extractor import BaseFeatureExtractor
                self._feature_extractor = BaseFeatureExtractor(history_size=25)
        return self._feature_extractor
    
    def _get_ensemble_predictor(self):
        """Ленивая загрузка ансамблевого предсказателя"""
        if self._ensemble_predictor is None:
            try:
                from ml.ensemble.ensemble import EnsemblePredictor
                self._ensemble_predictor = EnsemblePredictor()
            except ImportError as e:
                logger.warning(f"⚠️  Не удалось загрузить ансамблевый предсказатель: {e}")
                self._ensemble_predictor = None
        return self._ensemble_predictor
    
    def _get_pattern_analyzer(self):
        """Ленивая загрузка анализатора паттернов"""
        if self._pattern_analyzer is None:
            try:
                from ml.features.analyzer import AdvancedPatternAnalyzer
                self._pattern_analyzer = AdvancedPatternAnalyzer()
            except ImportError as e:
                logger.warning(f"⚠️  Не удалось загрузить анализатор паттернов: {e}")
                self._pattern_analyzer = None
        return self._pattern_analyzer
    
    def load_model(self) -> bool:
        """Загрузка обученной модели"""
        if not os.path.exists(self.model_path):
            logger.error(f"❌ Файл модели не найден: {self.model_path}")
            return False
            
        try:
            checkpoint = torch.load(self.model_path, weights_only=False, map_location='cpu')
            config = checkpoint['model_config']
            
            from ml.core.model import EnhancedNumberPredictor
            self.model = EnhancedNumberPredictor(
                input_size=config['input_size'],
                hidden_size=config['hidden_size']
            )
            self.model.load_state_dict(checkpoint['model_state_dict'])
            self.model.to(self.device)
            self.model.eval()
            
            self.is_trained = True
            
            # Обновляем ансамбль если доступен
            ensemble = self._get_ensemble_predictor()
            if ensemble:
                ensemble.set_neural_predictor(self)
                try:
                    from ml.utils.data_utils import load_dataset
                    dataset = load_dataset()
                    ensemble.update_ensemble(dataset)
                except Exception as e:
                    logger.warning(f"⚠️  Ошибка обновления ансамбля: {e}")
            
            logger.info(f"✅ УСИЛЕННАЯ нейросеть загружена: {self.model_path}")
            return True
            
        except Exception as e:
            logger.error(f"❌ Ошибка загрузки модели: {e}")
            return False
    
    def predict_group(self, number_history: List[int], top_k: int = None) -> List[Tuple[Tuple[int, int, int, int], float]]:
        """УСИЛЕННОЕ предсказание следующей группы чисел с ансамблевыми методами"""
        top_k = top_k or constants.PREDICTION_TOP_K
        
        # Используем ансамбль если включен и есть достаточно данных
        if self.use_ensemble and len(number_history) >= 30:
            try:
                ensemble = self._get_ensemble_predictor()
                if ensemble:
                    predictions = ensemble.predict_ensemble(number_history, top_k)
                    if predictions:
                        logger.info(f"🎯 Ансамбль сгенерировал {len(predictions)} предсказаний")
                        return predictions
            except Exception as e:
                logger.warning(f"⚠️  Ошибка ансамблевого предсказания, используем базовую модель: {e}")
        
        # Резервный вариант: оригинальная модель
        return self._predict_original(number_history, top_k)
    
    def _predict_original(self, number_history: List[int], top_k: int) -> List[Tuple[Tuple[int, int, int, int], float]]:
        """Оригинальный метод предсказания (как запасной вариант)"""
        if not self.is_trained or self.model is None:
            if not self.load_model():
                return []
        
        if len(number_history) < 25:
            logger.error("❌ Недостаточно данных в истории")
            return []
        
        feature_extractor = self._get_feature_extractor()
        features = feature_extractor.extract_features(number_history)
        features_tensor = torch.tensor(features, dtype=torch.float32).unsqueeze(0)
        
        with torch.no_grad():
            outputs = self.model(features_tensor)
            probabilities = torch.softmax(outputs, dim=-1)
            
            # Генерация кандидатов
            candidates = self._generate_enhanced_candidates(probabilities[0], top_k, number_history)
            return candidates
    
    def _generate_enhanced_candidates(self, probabilities: torch.Tensor, top_k: int, history: List[int]) -> List[Tuple[Tuple[int, int, int, int], float]]:
        """УСИЛЕННАЯ генерация кандидатных групп с улучшенной логикой"""
        logger.debug(f"🔍 Начало генерации кандидатов, top_k={top_k}")
        candidates = []
        
        # Глубокий анализ истории
        pattern_analysis = self._deep_pattern_analysis(history)
        
        # Генерация на основе модели
        model_candidates = self._generate_model_based_candidates(probabilities, 20, pattern_analysis)
        logger.debug(f"🔍 Модельные кандидаты: {len(model_candidates)}")
        candidates.extend(model_candidates)
        
        # Генерация на основе паттернов
        pattern_candidates = self._generate_intelligent_patterns(history, 15, pattern_analysis)
        candidates.extend(pattern_candidates)
        
        # Добавляем частотные кандидаты
        try:
            frequency_candidates = self._generate_frequency_based_candidates(history, 10)
            logger.debug(f"🔍 Частотные кандидаты: {len(frequency_candidates)}")
            candidates.extend(frequency_candidates)
        except Exception as e:
            logger.warning(f"⚠️  Ошибка генерации частотных кандидатов: {e}")
        
        # Сортировка и фильтрация
        candidates.sort(key=lambda x: x[1], reverse=True)
        
        # Убираем дубликаты
        unique_candidates = []
        seen = set()
        for group, score in candidates:
            if group not in seen:
                seen.add(group)
                unique_candidates.append((group, score))
            if len(unique_candidates) >= top_k * 2:
                break
        
        # Фильтрация по качеству
        filtered_candidates = self._filter_candidates_by_quality(unique_candidates, pattern_analysis)
        
        return filtered_candidates[:top_k]
    
    def _generate_frequency_based_candidates(self, history: List[int], count: int) -> List[tuple]:
        """Генерация кандидатов на основе частотного анализа"""
        try:
            from ml.utils.data_utils import load_dataset
            from ml.ensemble.patterns import FrequencyBasedPredictor
            
            dataset = load_dataset()
            if not dataset:
                return []
                
            freq_predictor = FrequencyBasedPredictor()
            freq_predictor.update_frequencies(dataset)
            
            candidates = []
            import random
            
            # Генерация групп с высокими вероятностными scores
            for _ in range(count * 5):
                group = (
                    random.randint(1, 26),
                    random.randint(1, 26),
                    random.randint(1, 26), 
                    random.randint(1, 26)
                )
                
                # Проверяем валидность
                if group[0] != group[1] and group[2] != group[3]:
                    score = freq_predictor.get_probability_scores(group)
                    if score > 1e-8:
                        candidates.append((group, score))
            
            # Возвращаем лучшие
            candidates.sort(key=lambda x: x[1], reverse=True)
            return candidates[:count]
            
        except Exception as e:
            logger.error(f"❌ Ошибка в частотной генерации: {e}")
            return []
    
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
            if abs(recent[i] - recent[i-1]) <= 2:
                current_seq.append(recent[i])
            else:
                if len(current_seq) >= 3:
                    sequences.append(current_seq)
                current_seq = [recent[i]]
        
        if len(current_seq) >= 3:
            sequences.append(current_seq)
        
        # Временной анализ
        temporal_patterns = {}
        analyzer = self._get_pattern_analyzer()
        if analyzer:
            try:
                temporal_patterns = analyzer.analyze_time_series(history)
            except Exception as e:
                logger.warning(f"⚠️  Ошибка анализа временных паттернов: {e}")
        
        return {
            'hot_numbers': hot_numbers,
            'cold_numbers': cold_numbers,
            'sequences': sequences,
            'frequencies': freq,
            'recent_numbers': recent,
            'temporal_patterns': temporal_patterns
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
        generated = 0
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
                        pattern_score = self._calculate_enhanced_pattern_score(group, pattern_analysis)
                        adjusted_score = base_score * pattern_score
                        
                        # Усиливаем хорошие предсказания
                        if adjusted_score > 0.0001:
                            adjusted_score *= 2
                        
                        candidates.append((group, adjusted_score))
                        generated += 1
                        
                        if generated >= count * 10:
                            return candidates
        
        return candidates
    
    def _calculate_enhanced_pattern_score(self, group: Tuple[int, int, int, int], pattern_analysis: dict) -> float:
        """Расчет усиленного pattern score с новыми факторами"""
        score = 1.0
        hot_numbers = pattern_analysis.get('hot_numbers', [])
        cold_numbers = pattern_analysis.get('cold_numbers', [])
        temporal_patterns = pattern_analysis.get('temporal_patterns', {})
        
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
        
        # Учет временных паттернов
        autocorr = temporal_patterns.get('autocorrelation', {})
        if autocorr:
            avg_autocorr = sum(autocorr.values()) / len(autocorr)
            if avg_autocorr > 0.3:
                # При высокой автокорреляции предпочитаем группы с числами из истории
                history_overlap = sum(1 for num in group if num in pattern_analysis.get('recent_numbers', []))
                score *= (1 + history_overlap * 0.2)
        
        return score
    
    def _generate_intelligent_patterns(self, history: List[int], count: int, pattern_analysis: dict) -> List[Tuple[Tuple[int, int, int, int], float]]:
        """Генерация интеллектуальных паттернов с улучшениями"""
        candidates = []
        import random
        
        hot_numbers = pattern_analysis.get('hot_numbers', [])
        cold_numbers = pattern_analysis.get('cold_numbers', [])
        sequences = pattern_analysis.get('sequences', [])
        
        strategies = [
            lambda: self._strategy_mixed_hot_cold(hot_numbers, cold_numbers),
            lambda: self._strategy_balanced_ranges(),
            lambda: self._strategy_follow_sequences(sequences),
            lambda: self._strategy_avoid_recent(pattern_analysis.get('recent_numbers', [])),
            lambda: self._strategy_temporal_patterns(pattern_analysis.get('temporal_patterns', {})),
        ]
        
        for _ in range(count):
            strategy = random.choice(strategies)
            group = strategy()
            
            if group and group not in [c[0] for c in candidates]:
                base_score = 0.001
                
                # Повышаем score для стратегий с временными паттернами
                if strategy == strategies[-1]:
                    base_score *= 1.5
                
                candidates.append((group, base_score))
        
        return candidates
    
    def _strategy_temporal_patterns(self, temporal_patterns: dict) -> Tuple[int, int, int, int]:
        """Стратегия: учет временных паттернов"""
        import random
        
        trending = temporal_patterns.get('linear_trend', 0)
        mean_reversion = temporal_patterns.get('mean_reversion', 0)
        
        if abs(trending) > 0.1:
            # Стратегия следования тренду
            base_num = random.randint(8, 18)
            trend_adjusted = [max(1, min(26, int(base_num + trending * i))) for i in range(4)]
            return self._create_valid_group(trend_adjusted)
        elif mean_reversion > 1.0:
            # Стратегия возвращения к среднему
            mean_val = 13.5
            reversion_nums = [max(1, min(26, int(mean_val + random.uniform(-5, 5)))) for _ in range(4)]
            return self._create_valid_group(reversion_nums)
        else:
            return self._strategy_balanced_ranges()
    
    def _strategy_mixed_hot_cold(self, hot_numbers: List[int], cold_numbers: List[int]) -> Tuple[int, int, int, int]:
        """Стратегия: смесь горячих и холодных чисел"""
        import random
        
        if not cold_numbers:
            cold_numbers = [n for n in range(1, 27) if n not in hot_numbers] if hot_numbers else list(range(1, 27))
        if not hot_numbers:
            hot_numbers = [n for n in range(1, 27) if n not in cold_numbers] if cold_numbers else list(range(1, 27))
        
        cold_count = random.choice([2, 3])
        hot_count = 4 - cold_count
        
        cold_choices = random.sample(cold_numbers, min(cold_count, len(cold_numbers)))
        hot_choices = random.sample(hot_numbers, min(hot_count, len(hot_numbers)))
        
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
            last_seq = sequences[-1]
            if len(last_seq) >= 2:
                base_num = last_seq[-1]
                next_nums = [base_num + 1, base_num - 1, base_num + 2, base_num - 2]
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
        
        avoid_set = set(recent[-8:])
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
            all_nums = list(range(1, 27))
            additional = [n for n in all_nums if n not in numbers]
            numbers.extend(random.sample(additional, 4 - len(numbers)))
        
        first_pair = numbers[:2]
        second_pair = numbers[2:4]
        
        if first_pair[0] == first_pair[1]:
            first_pair[1] = random.choice([n for n in range(1, 27) if n != first_pair[0]])
        if second_pair[0] == second_pair[1]:
            second_pair[1] = random.choice([n for n in range(1, 27) if n != second_pair[0]])
        
        return (first_pair[0], first_pair[1], second_pair[0], second_pair[1])
    
    def _filter_candidates_by_quality(self, candidates: List[tuple], pattern_analysis: dict) -> List[tuple]:
        """Фильтрация кандидатов по качеству"""
        filtered = []
        
        for group, score in candidates:
            quality_score = self._calculate_quality_score(group, pattern_analysis)
            final_score = score * quality_score
            
            if final_score > 0.00005:
                filtered.append((group, final_score))
        
        filtered.sort(key=lambda x: x[1], reverse=True)
        return filtered
    
    def _calculate_quality_score(self, group: Tuple[int, int, int, int], pattern_analysis: dict) -> float:
        """Расчет score качества группы"""
        score = 1.0
        
        if len(set(group)) < 4:
            score *= 0.5
        
        even_count = sum(1 for num in group if num % 2 == 0)
        if even_count == 0 or even_count == 4:
            score *= 0.7
        
        low_count = sum(1 for num in group if num <= 13)
        if low_count == 0 or low_count == 4:
            score *= 0.8
        
        temporal_patterns = pattern_analysis.get('temporal_patterns', {})
        hurst = temporal_patterns.get('hurst_exponent', 0.5)
        
        if hurst > 0.7:
            recent_avg = np.mean(pattern_analysis.get('recent_numbers', [13.5]))
            group_avg = np.mean(group)
            if abs(group_avg - recent_avg) < 3:
                score *= 1.2
        
        return score
    
    def enable_ensemble(self, enable: bool = True):
        """Включение/выключение ансамблевого режима"""
        self.use_ensemble = enable