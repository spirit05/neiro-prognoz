# /opt/model/ml/ensemble/predictors/frequency.py
"""
FrequencyPredictor - ИСПРАВЛЕННАЯ ВЕРСИЯ
"""

import numpy as np
from typing import List, Tuple, Dict
import logging
from pathlib import Path
import random

from ml.core.base_model import AbstractBaseModel
from ml.core.types import (
    ModelType, ModelStatus, TrainingConfig, 
    ModelMetadata, TrainingResult, PredictionResponse,
    DataBatch, FeatureSpec
)


class FrequencyPredictor(AbstractBaseModel):
    """Частотный предсказатель - ИСПРАВЛЕННАЯ ВЕРСИЯ"""
    
    def __init__(self, model_id: str = "frequency_predictor"):
        super().__init__(model_id, ModelType.CLASSIFICATION)
        
        self.number_frequencies: Dict[int, int] = {}
        self.pair_frequencies: Dict[Tuple[int, int], int] = {}
        self.position_frequencies: Dict[int, Dict[int, int]] = {0: {}, 1: {}, 2: {}, 3: {}}
        self.total_groups = 0
        
        self._feature_specs = self._create_feature_specs()
        
        self.logger.info("📈 Инициализирован FrequencyPredictor (исправленная версия)")

    def _create_feature_specs(self) -> List[FeatureSpec]:
        """Создание спецификаций фич"""
        return [
            FeatureSpec(name="total_groups", dtype="int", required=True),
            FeatureSpec(name="unique_numbers", dtype="int", required=True)
        ]

    def train(self, data: DataBatch, config: TrainingConfig) -> TrainingResult:
        """Обучение на основе частотного анализа - ИСПРАВЛЕННАЯ ВЕРСИЯ"""
        self.logger.info("🔄 Обучение FrequencyPredictor (частотный анализ)")
        
        # Сбрасываем частоты
        self._reset_frequencies()
        
        # Анализируем данные для построения частотных распределений
        dataset = self._extract_dataset_from_batch(data)
        self._update_frequencies(dataset)
        
        self._is_trained = True
        self.status = ModelStatus.TRAINED
        
        metrics = {
            'total_groups_analyzed': self.total_groups,
            'unique_numbers': len(self.number_frequencies),
            'unique_pairs': len(self.pair_frequencies)
        }
        
        self.logger.info(f"📊 Проанализировано {self.total_groups} групп, {len(self.number_frequencies)} уникальных чисел")
        
        return TrainingResult(
            model_id=self.model_id,
            status=self.status,
            metrics=metrics
        )

    def predict(self, data: DataBatch) -> PredictionResponse:
        """Предсказание на основе частотного анализа - ИСПРАВЛЕННАЯ ВЕРСИЯ"""
        if not self._is_trained:
            raise ValueError("Модель не обучена")
        
        if self.total_groups == 0:
            self.logger.warning("⚠️ Нет данных для частотного анализа")
            return PredictionResponse(
                predictions=[],
                model_id=self.model_id,
                inference_time=0.0
            )
        
        # Генерация кандидатов на основе частот
        candidates = self._generate_frequency_candidates(top_k=10)
        
        predictions = [group for group, score in candidates]
        probabilities = [[score] for group, score in candidates]
        
        self.logger.info(f"📊 Сгенерировано {len(predictions)} частотных прогнозов")
        
        return PredictionResponse(
            predictions=predictions,
            probabilities=probabilities,
            model_id=self.model_id,
            inference_time=0.0
        )

    def _extract_dataset_from_batch(self, data: DataBatch) -> List[List[int]]:
        """Извлечение датасета из DataBatch - ИСПРАВЛЕННАЯ ВЕРСИЯ"""
        dataset = []
        
        try:
            if hasattr(data.data, 'values'):
                # Обрабатываем DataFrame - каждая строка это группа из 4 чисел
                for index, row in data.data.iterrows():
                    if len(row) >= 4:
                        # Преобразуем в список чисел
                        group = [int(float(x)) for x in row[:4] if not np.isnan(float(x))]
                        if len(group) == 4 and self._validate_group(group):
                            dataset.append(group)
                self.logger.info(f"📥 Извлечено {len(dataset)} групп из DataFrame")
            else:
                self.logger.warning(f"⚠️ Неизвестный формат данных: {type(data.data)}")
        except Exception as e:
            self.logger.error(f"❌ Ошибка извлечения датасета: {e}")
        
        return dataset

    def _update_frequencies(self, dataset: List[List[int]]):
        """Обновление частотных характеристик - ИСПРАВЛЕННАЯ ВЕРСИЯ"""
        self.position_frequencies = {0: {}, 1: {}, 2: {}, 3: {}}
        self.pair_frequencies = {}
        self.number_frequencies = {}
        
        all_numbers = []
        self.total_groups = len(dataset)
        
        for group in dataset:
            if len(group) != 4:
                continue
                
            all_numbers.extend(group)
            
            # Частоты чисел по позициям
            for i, num in enumerate(group):
                self.position_frequencies[i][num] = self.position_frequencies[i].get(num, 0) + 1
            
            # Частоты пар (сортированные для consistency)
            pair1 = tuple(sorted(group[:2]))
            pair2 = tuple(sorted(group[2:]))
            self.pair_frequencies[pair1] = self.pair_frequencies.get(pair1, 0) + 1
            self.pair_frequencies[pair2] = self.pair_frequencies.get(pair2, 0) + 1
        
        # Общие частоты чисел
        for num in all_numbers:
            self.number_frequencies[num] = self.number_frequencies.get(num, 0) + 1

    def _generate_frequency_candidates(self, top_k: int) -> List[Tuple[Tuple[int, int, int, int], float]]:
        """Генерация кандидатов на основе частот - ИСПРАВЛЕННАЯ ВЕРСИЯ"""
        candidates = []
        
        # Стратегия 1: Самые частые числа
        most_common_numbers = sorted(self.number_frequencies.items(), key=lambda x: x[1], reverse=True)[:8]
        
        if most_common_numbers:
            common_nums = [num for num, freq in most_common_numbers]
            # Создаем группы из самых частых чисел
            for i in range(min(5, len(common_nums))):
                for j in range(i+1, min(7, len(common_nums))):
                    base_group = [common_nums[i], common_nums[j]]
                    group = self._complete_group(base_group)
                    if group and group not in [c[0] for c in candidates]:
                        score = self._calculate_group_score(group)
                        candidates.append((group, score))
        
        # Стратегия 2: Самые частые пары
        most_common_pairs = sorted(self.pair_frequencies.items(), key=lambda x: x[1], reverse=True)[:5]
        
        for pair1, freq1 in most_common_pairs:
            for pair2, freq2 in most_common_pairs:
                if pair1 != pair2:
                    group = tuple(list(pair1) + list(pair2))
                    if self._validate_group(group) and group not in [c[0] for c in candidates]:
                        score = self._calculate_group_score(group)
                        candidates.append((group, score))
        
        # Стратегия 3: Случайные группы с учетом частот
        if len(candidates) < top_k:
            needed = top_k - len(candidates)
            for i in range(needed * 3):
                group = self._generate_weighted_group()
                if group and group not in [c[0] for c in candidates]:
                    score = self._calculate_group_score(group) * 0.5  # Понижаем score для случайных
                    candidates.append((group, score))
        
        # Сортируем по score и возвращаем лучшие
        candidates.sort(key=lambda x: x[1], reverse=True)
        return candidates[:top_k]

    def _calculate_group_score(self, group: Tuple[int, int, int, int]) -> float:
        """Расчет score для группы на основе частот"""
        if self.total_groups == 0:
            return 0.001
        
        score = 1.0
        
        # Вероятности по позициям
        for i, num in enumerate(group):
            pos_freq = self.position_frequencies[i].get(num, 0)
            # Additive smoothing
            score *= (pos_freq + 1) / (self.total_groups + 26)
        
        # Вероятности пар
        pair1 = tuple(sorted(group[:2]))
        pair2 = tuple(sorted(group[2:]))
        
        total_pairs = self.total_groups
        pair1_prob = (self.pair_frequencies.get(pair1, 0) + 1) / (total_pairs + 325)
        pair2_prob = (self.pair_frequencies.get(pair2, 0) + 1) / (total_pairs + 325)
        
        score *= pair1_prob * pair2_prob
        
        return max(1e-10, score)

    def _complete_group(self, base_numbers: List[int]) -> Tuple[int, int, int, int]:
        """Дополнение группы до 4 чисел"""
        if len(base_numbers) >= 4:
            return self._create_valid_group(base_numbers[:4])
        
        group = list(set(base_numbers))  # Убираем дубликаты
        all_nums = list(range(1, 27))
        available = [n for n in all_nums if n not in group]
        
        # Добираем до 4 чисел
        while len(group) < 4 and available:
            # Предпочтение более частым числам
            weights = [self.number_frequencies.get(n, 1) for n in available]
            total_weight = sum(weights)
            if total_weight > 0:
                probs = [w/total_weight for w in weights]
                next_num = np.random.choice(available, p=probs)
            else:
                next_num = random.choice(available)
            
            group.append(next_num)
            available.remove(next_num)
        
        return self._create_valid_group(group)

    def _generate_weighted_group(self) -> Tuple[int, int, int, int]:
        """Генерация группы с учетом весов чисел"""
        all_nums = list(range(1, 27))
        weights = [self.number_frequencies.get(n, 1) for n in all_nums]
        
        # Выбираем 4 числа с учетом весов
        group = []
        available = all_nums.copy()
        available_weights = weights.copy()
        
        for _ in range(4):
            if not available:
                break
                
            total_weight = sum(available_weights)
            if total_weight > 0:
                probs = [w/total_weight for w in available_weights]
                chosen_idx = np.random.choice(len(available), p=probs)
            else:
                chosen_idx = random.randint(0, len(available)-1)
            
            group.append(available[chosen_idx])
            # Удаляем выбранное число
            available.pop(chosen_idx)
            available_weights.pop(chosen_idx)
        
        return self._create_valid_group(group)

    def _create_valid_group(self, numbers: List[int]) -> Tuple[int, int, int, int]:
        """Создание валидной группы"""
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

    def _validate_group(self, group) -> bool:
        """Валидация группы чисел"""
        try:
            if len(group) != 4:
                return False
            if not all(1 <= x <= 26 for x in group):
                return False
            if group[0] == group[1] or group[2] == group[3]:
                return False
            return True
        except:
            return False

    def _reset_frequencies(self) -> None:
        """Сброс частотных данных"""
        self.number_frequencies = {}
        self.pair_frequencies = {}
        self.position_frequencies = {0: {}, 1: {}, 2: {}, 3: {}}
        self.total_groups = 0


    def save(self, path: Path) -> None:
        """Сохранение частотных данных"""
        config = {
            'model_id': self.model_id,
            'model_type': self.model_type.value,
            'total_groups': self.total_groups,
            'number_frequencies': self.number_frequencies,
            'pair_frequencies': {str(k): v for k, v in self.pair_frequencies.items()},
            'position_frequencies': {str(k): v for k, v in self.position_frequencies.items()},
            'is_trained': self._is_trained
        }
        
        import json
        with open(path / "config.json", 'w', encoding='utf-8') as f:
            json.dump(config, f, indent=2, ensure_ascii=False)
        
        self.logger.info(f"💾 FrequencyPredictor сохранен: {path}")

    def load(self, path: Path) -> None:
        """Загрузка частотных данных"""
        config_path = path / "config.json"
        
        if not config_path.exists():
            raise FileNotFoundError(f"Конфигурация не найдена: {config_path}")
        
        import json
        with open(config_path, 'r', encoding='utf-8') as f:
            config = json.load(f)
        
        self.total_groups = config.get('total_groups', 0)
        self.number_frequencies = config.get('number_frequencies', {})
        
        # Восстанавливаем пары
        pair_frequencies = config.get('pair_frequencies', {})
        self.pair_frequencies = {}
        for k, v in pair_frequencies.items():
            try:
                pair_tuple = tuple(map(int, k.strip('()').split(',')))
                self.pair_frequencies[pair_tuple] = v
            except:
                continue
        
        # Восстанавливаем позиционные частоты
        position_frequencies = config.get('position_frequencies', {})
        self.position_frequencies = {}
        for k, v in position_frequencies.items():
            self.position_frequencies[int(k)] = v
        
        self._is_trained = config.get('is_trained', False)
        self.status = ModelStatus.READY if self._is_trained else ModelStatus.FAILED
        
        self.logger.info(f"📥 FrequencyPredictor загружен: {path}")
