# /opt/model/ml/ensemble/predictors/pattern_based.py
"""
PatternBasedPredictor - ИСПРАВЛЕННАЯ ВЕРСИЯ
"""

import numpy as np
from typing import List, Tuple
import logging
from pathlib import Path
import random

from ml.core.base_model import AbstractBaseModel
from ml.core.types import (
    ModelType, ModelStatus, TrainingConfig, 
    ModelMetadata, TrainingResult, PredictionResponse,
    DataBatch, FeatureSpec
)


class PatternBasedPredictor(AbstractBaseModel):
    """Предсказатель на основе паттернов последовательностей - ИСПРАВЛЕННАЯ ВЕРСИЯ"""
    
    def __init__(self, model_id: str = "pattern_based_predictor"):
        super().__init__(model_id, ModelType.CLASSIFICATION)
        
        self._feature_specs = self._create_feature_specs()
        
        self.logger.info("🔍 Инициализирован PatternBasedPredictor (исправленная версия)")

    def _create_feature_specs(self) -> List[FeatureSpec]:
        """Создание спецификаций фич"""
        return [
            FeatureSpec(name="sequence_analysis", dtype="float", required=True)
        ]

    def train(self, data: DataBatch, config: TrainingConfig) -> TrainingResult:
        """Обучение - паттернные методы не требуют традиционного обучения"""
        self.logger.info("🔄 Анализ паттернов для PatternBasedPredictor")
        
        # Анализируем данные для выявления типичных паттернов
        history = self._extract_history_from_batch(data)
        if len(history) > 0:
            sequences = self._find_sequences(history)
            self.logger.info(f"📊 Обнаружено {len(sequences)} последовательностей")
        
        self._is_trained = True
        self.status = ModelStatus.TRAINED
        
        return TrainingResult(
            model_id=self.model_id,
            status=self.status,
            metrics={'patterns_analyzed': True}
        )

    def predict(self, data: DataBatch) -> PredictionResponse:
        """Предсказание на основе паттернов - ИСПРАВЛЕННАЯ ВЕРСИЯ"""
        if not self._is_trained:
            raise ValueError("Модель не обучена")
        
        history = self._extract_history_from_batch(data)
        
        # Уменьшаем минимальную длину истории для тестирования
        if len(history) < 8:
            self.logger.warning(f"⚠️ История слишком короткая: {len(history)} чисел")
            return PredictionResponse(
                predictions=[],
                model_id=self.model_id,
                inference_time=0.0
            )
        
        # Генерация кандидатов на основе паттернов
        candidates = self._generate_pattern_candidates(history, top_k=10)
        
        predictions = [group for group, score in candidates]
        probabilities = [[score] for group, score in candidates]
        
        self.logger.info(f"🔍 Сгенерировано {len(predictions)} паттернных прогнозов")
        
        return PredictionResponse(
            predictions=predictions,
            probabilities=probabilities,
            model_id=self.model_id,
            inference_time=0.0
        )

    def _extract_history_from_batch(self, data: DataBatch) -> List[int]:
        """Извлечение истории из DataBatch - ИСПРАВЛЕННАЯ ВЕРСИЯ"""
        try:
            if hasattr(data.data, 'values'):
                # Преобразуем все данные в один плоский список
                flattened = data.data.values.flatten()
                # Фильтруем NaN значения и преобразуем в int
                filtered = [int(x) for x in flattened if not np.isnan(x)]
                return filtered
            else:
                self.logger.warning(f"⚠️ Неизвестный формат данных: {type(data.data)}")
                return []
        except Exception as e:
            self.logger.error(f"❌ Ошибка извлечения истории: {e}")
            return []

    def _generate_pattern_candidates(self, history: List[int], top_k: int) -> List[Tuple[Tuple[int, int, int, int], float]]:
        """Генерация кандидатов на основе паттернов - ИСПРАВЛЕННАЯ ВЕРСИЯ"""
        candidates = []
        
        # Стратегия 1: Анализ последовательностей
        sequences = self._find_sequences(history)
        self.logger.info(f"🔍 Найдено последовательностей: {len(sequences)}")
        
        for seq in sequences[-5:]:  # Берем последние 5 последовательностей
            if len(seq) >= 2:
                # Продолжаем последовательность
                last_num = seq[-1]
                # Более широкий диапазон для продолжения
                possible_next = [
                    last_num + 1, last_num - 1, 
                    last_num + 2, last_num - 2,
                    last_num + 3, last_num - 3
                ]
                valid_next = [n for n in possible_next if 1 <= n <= 26 and n not in seq[-3:]]
                
                if valid_next:
                    for next_num in valid_next[:2]:  # Берем до 2 продолжений
                        base_group = [last_num, next_num]
                        group = self._complete_group(base_group)
                        if group and group not in [c[0] for c in candidates]:
                            candidates.append((group, 0.005))
        
        # Стратегия 2: Повторяющиеся паттерны
        if len(history) >= 10:
            recent = history[-10:]
            # Ищем часто встречающиеся числа в последних данных
            from collections import Counter
            freq = Counter(recent)
            common_nums = [num for num, count in freq.most_common(4) if count >= 2]
            
            if len(common_nums) >= 2:
                group = self._complete_group(common_nums[:2])
                if group and group not in [c[0] for c in candidates]:
                    candidates.append((group, 0.004))
        
        # Стратегия 3: Резервная случайная генерация
        if len(candidates) < top_k:
            needed = top_k - len(candidates)
            for i in range(needed * 2):  # Генерируем больше для выбора лучших
                group = self._create_random_group()
                if group and group not in [c[0] for c in candidates]:
                    score = 0.001 * (1 - i * 0.01)  # Уменьшаем score для более поздних кандидатов
                    candidates.append((group, score))
        
        # Сортируем по score и возвращаем лучшие
        candidates.sort(key=lambda x: x[1], reverse=True)
        return candidates[:top_k]

    def _find_sequences(self, history: List[int]) -> List[List[int]]:
        """Поиск последовательностей в истории - ИСПРАВЛЕННАЯ ВЕРСИЯ"""
        if len(history) < 3:
            return []
            
        sequences = []
        current_seq = [history[0]]
        
        for i in range(1, len(history)):
            diff = abs(history[i] - history[i-1])
            # Более либеральные условия для последовательностей
            if diff <= 3:  # Увеличили шаг до 3
                current_seq.append(history[i])
            else:
                if len(current_seq) >= 2:  # Уменьшили минимальную длину до 2
                    sequences.append(current_seq.copy())
                current_seq = [history[i]]
        
        if len(current_seq) >= 2:
            sequences.append(current_seq)
        
        return sequences

    def _complete_group(self, base_numbers: List[int]) -> Tuple[int, int, int, int]:
        """Дополнение группы до 4 чисел"""
        if len(base_numbers) >= 4:
            return self._create_valid_group(base_numbers[:4])
        
        # Создаем полную группу из базовых чисел
        group = list(set(base_numbers))  # Убираем дубликаты
        all_nums = list(range(1, 27))
        available = [n for n in all_nums if n not in group]
        
        # Добираем до 4 чисел
        while len(group) < 4 and available:
            group.append(available.pop(random.randint(0, len(available)-1)))
        
        return self._create_valid_group(group)

    def _create_random_group(self) -> Tuple[int, int, int, int]:
        """Создание случайной валидной группы"""
        all_nums = list(range(1, 27))
        group = random.sample(all_nums, 4)
        return self._create_valid_group(group)

    def _create_valid_group(self, numbers: List[int]) -> Tuple[int, int, int, int]:
        """Создание валидной группы - ИСПРАВЛЕННАЯ ВЕРСИЯ"""
        if len(numbers) < 4:
            return None
            
        # Убеждаемся, что в парах нет одинаковых чисел
        first_pair = numbers[:2]
        second_pair = numbers[2:4]
        
        # Исправляем одинаковые числа в парах
        if first_pair[0] == first_pair[1]:
            alternatives = [n for n in range(1, 27) if n != first_pair[0] and n not in second_pair]
            if alternatives:
                first_pair = (first_pair[0], random.choice(alternatives))
            else:
                return None
                
        if second_pair[0] == second_pair[1]:
            alternatives = [n for n in range(1, 27) if n != second_pair[0] and n not in first_pair]
            if alternatives:
                second_pair = (second_pair[0], random.choice(alternatives))
            else:
                return None
        
        return (first_pair[0], first_pair[1], second_pair[0], second_pair[1])

    def save(self, path: Path) -> None:
        """Сохранение модели"""
        config = {
            'model_id': self.model_id,
            'model_type': self.model_type.value,
            'metadata': self.metadata.model_dump(),
            'is_trained': self._is_trained
        }
        
        import json
        with open(path / "config.json", 'w', encoding='utf-8') as f:
            json.dump(config, f, indent=2, ensure_ascii=False)
        
        self.logger.info(f"💾 PatternBasedPredictor сохранен: {path}")

    def load(self, path: Path) -> None:
        """Загрузка модели"""
        config_path = path / "config.json"
        
        if not config_path.exists():
            raise FileNotFoundError(f"Конфигурация не найдена: {config_path}")
        
        import json
        with open(config_path, 'r', encoding='utf-8') as f:
            config = json.load(f)
        
        self._is_trained = config.get('is_trained', False)
        self.status = ModelStatus.READY if self._is_trained else ModelStatus.FAILED
        
        self.logger.info(f"📥 PatternBasedPredictor загружен: {path}")
