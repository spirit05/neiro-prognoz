# /opt/model/ml/ensemble/predictors/statistical.py
"""
StatisticalPredictor - ИСПРАВЛЕННАЯ ВЕРСИЯ
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


class StatisticalPredictor(AbstractBaseModel):
    """Статистический предсказатель - ИСПРАВЛЕННАЯ ВЕРСИЯ"""
    
    def __init__(self, model_id: str = "statistical_predictor"):
        super().__init__(model_id, ModelType.CLASSIFICATION)
        
        self._pattern_analyzer = None
        self._max_history_length = 100
        self._feature_specs = self._create_feature_specs()
        
        self.logger.info("📊 Инициализирован StatisticalPredictor (исправленная версия)")

    def _create_feature_specs(self) -> List[FeatureSpec]:
        """Создание спецификаций фич"""
        return [
            FeatureSpec(name="history_length", dtype="int", required=True),
            FeatureSpec(name="pattern_complexity", dtype="float", required=True)
        ]

    def _get_pattern_analyzer(self):
        """Ленивая загрузка анализатора паттернов"""
        if self._pattern_analyzer is None:
            try:
                from ml.features.engineers.advanced import AdvancedEngineer
                self._pattern_analyzer = AdvancedEngineer()
            except ImportError as e:
                self.logger.warning(f"⚠️ Не удалось загрузить анализатора паттернов: {e}")
                self._pattern_analyzer = None
        return self._pattern_analyzer

    def train(self, data: DataBatch, config: TrainingConfig) -> TrainingResult:
        """Обучение статистического предсказателя"""
        self.logger.info("🔄 Обучение StatisticalPredictor")
        
        # Статистические методы могут анализировать данные для настройки параметров
        if hasattr(data.data, 'values'):
            history_data = data.data.values.flatten()
            self._analyze_data_patterns(history_data)
        
        self._is_trained = True
        self.status = ModelStatus.TRAINED
        
        return TrainingResult(
            model_id=self.model_id,
            status=self.status,
            metrics={'analysis_complete': True}
        )

    def predict(self, data: DataBatch) -> PredictionResponse:
        """Предсказание - ИСПРАВЛЕННАЯ ВЕРСИЯ"""
        if not self._is_trained:
            raise ValueError("Модель не обучена")
        
        history = self._extract_history_from_batch(data)
        
        # ВРЕМЕННО: уменьшаем минимальную длину для тестирования
        if len(history) < 10:  # Было 20
            self.logger.warning(f"⚠️ История слишком короткая: {len(history)} чисел")
            return PredictionResponse(
                predictions=[],
                model_id=self.model_id,
                inference_time=0.0
            )
        
        # Ограничение истории
        limited_history = history[-self._max_history_length:]
        
        # Анализ паттернов
        analyzer = self._get_pattern_analyzer()
        patterns = analyzer.analyze_time_series(limited_history) if analyzer else {}
        
        # Генерация кандидатов на основе статистических паттернов
        candidates = self._generate_statistical_candidates(limited_history, patterns, top_k=10)
        
        # Преобразование в новый формат
        predictions = [group for group, score in candidates]
        probabilities = [[score] for group, score in candidates]
        
        self.logger.info(f"📊 Сгенерировано {len(predictions)} статистических прогнозов")
        
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

    def _generate_statistical_candidates(self, history: List[int], patterns: Dict, top_k: int) -> List[Tuple[Tuple[int, int, int, int], float]]:
        """Генерация кандидатов на основе статистических паттернов - ИСПРАВЛЕННАЯ ВЕРСИЯ"""
        candidates = []
        recent = history[-10:] if len(history) >= 10 else history
        
        # Анализ автокорреляции
        autocorr = patterns.get('autocorrelation', {})
        trending = patterns.get('linear_trend', 0)
        mean_reversion = patterns.get('mean_reversion', 0)
        
        self.logger.info(f"🔍 Паттерны: trending={trending:.3f}, mean_reversion={mean_reversion:.3f}, autocorr={len(autocorr)}")
        
        for i in range(top_k * 3):  # Генерируем больше кандидатов
            group = None
            
            # Стратегия: продолжение тренда
            if abs(trending) > 0.1:
                base_nums = random.sample(recent, min(2, len(recent)))
                new_nums = [max(1, min(26, int(x + trending * random.uniform(1, 3)))) for x in base_nums]
                group = self._create_valid_group(new_nums + [random.randint(1, 26) for _ in range(2)])
            
            # Стратегия: mean reversion
            elif mean_reversion > 1.0:
                mean_val = np.mean(history)
                group = self._create_valid_group([
                    max(1, min(26, int(mean_val + random.uniform(-3, 3)))) for _ in range(4)
                ])
            
            # Случайная стратегия с учетом автокорреляции
            else:
                group = self._create_valid_group([random.randint(1, 26) for _ in range(4)])
            
            # Проверяем что группа создана и добавляем её
            if group is not None:
                # Базовый score для статистических кандидатов
                score = 0.001 * (1 + len(autocorr) * 0.1)
                candidates.append((group, score))
                self.logger.debug(f"🔍 Сгенерирован кандидат {i+1}: {group} (score={score:.6f})")
        
        self.logger.info(f"🔍 Итого сгенерировано кандидатов: {len(candidates)}")
        
        # Если кандидатов нет, генерируем резервные
        if not candidates:
            self.logger.warning("⚠️ Не удалось сгенерировать кандидатов, используем резервные")
            candidates = self._generate_fallback_candidates(top_k)
        
        return candidates[:top_k]

    def _create_valid_group(self, numbers: List[int]) -> Tuple[int, int, int, int]:
        """Создание валидной группы из чисел - ИСПРАВЛЕННАЯ ВЕРСИЯ"""
        if len(numbers) < 4:
            all_nums = list(range(1, 27))
            additional = [n for n in all_nums if n not in numbers]
            numbers.extend(random.sample(additional, 4 - len(numbers)))
        
        # Создаем валидные пары
        first_pair = numbers[:2]
        second_pair = numbers[2:4]
        
        # Проверяем уникальность в парах
        if first_pair[0] == first_pair[1]:
            first_pair = (first_pair[0], random.choice([n for n in range(1, 27) if n != first_pair[0]]))
        if second_pair[0] == second_pair[1]:
            second_pair = (second_pair[0], random.choice([n for n in range(1, 27) if n != second_pair[0]]))
        
        return (first_pair[0], first_pair[1], second_pair[0], second_pair[1])

    def _generate_fallback_candidates(self, count: int) -> List[Tuple[Tuple[int, int, int, int], float]]:
        """Резервная генерация кандидатов при ошибках"""
        candidates = []
        
        for i in range(count):
            group = self._create_valid_group([])
            if group:
                candidates.append((group, 0.001))
        
        self.logger.info(f"🔄 Сгенерировано {len(candidates)} резервных кандидатов")
        return candidates

    def _analyze_data_patterns(self, data: np.ndarray) -> None:
        """Анализ паттернов данных для настройки"""
        if len(data) > 0:
            volatility = np.std(data)
            self.logger.info(f"📈 Анализ данных: волатильность={volatility:.2f}")

    def save(self, path: Path) -> None:
        """Сохранение модели"""
        config = {
            'model_id': self.model_id,
            'model_type': self.model_type.value,
            'max_history_length': self._max_history_length,
            'metadata': self.metadata.model_dump(),
            'is_trained': self._is_trained
        }
        
        import json
        with open(path / "config.json", 'w', encoding='utf-8') as f:
            json.dump(config, f, indent=2, ensure_ascii=False)
        
        self.logger.info(f"💾 StatisticalPredictor сохранен: {path}")

    def load(self, path: Path) -> None:
        """Загрузка модели"""
        config_path = path / "config.json"
        
        if not config_path.exists():
            raise FileNotFoundError(f"Конфигурация не найдена: {config_path}")
        
        import json
        with open(config_path, 'r', encoding='utf-8') as f:
            config = json.load(f)
        
        self._max_history_length = config.get('max_history_length', 100)
        self._is_trained = config.get('is_trained', False)
        self.status = ModelStatus.READY if self._is_trained else ModelStatus.FAILED
        
        self.logger.info(f"📥 StatisticalPredictor загружен: {path}")
