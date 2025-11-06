# ml/ensemble/ensemble.py
"""
Ансамблевые методы предсказания - РЕАЛЬНАЯ РЕАЛИЗАЦИЯ
"""

import random
from typing import List, Tuple
from config.logging_config import setup_logging

logger = setup_logging('EnsemblePredictor')

class EnsemblePredictor:
    def __init__(self):
        self.neural_predictor = None
        self.statistical_predictor = None
        logger.info("✅ EnsemblePredictor инициализирован")

    def set_neural_predictor(self, predictor):
        """Установка нейросетевого предсказателя"""
        self.neural_predictor = predictor

    def predict_ensemble(self, recent_numbers: List[int], top_k: int = 10) -> List[Tuple[Tuple[int, int, int, int], float]]:
        """Ансамблевое предсказание с комбинацией методов"""
        all_predictions = []

        # 1. Нейросетевые предсказания (если доступны)
        if self.neural_predictor and hasattr(self.neural_predictor, 'predict_group'):
            try:
                neural_predictions = self.neural_predictor.predict_group(recent_numbers, top_k * 2)
                # Увеличиваем вес нейросетевых предсказаний
                neural_predictions = [(group, score * 0.6, 'neural') for group, score in neural_predictions]
                all_predictions.extend(neural_predictions)
                logger.info(f"🔮 Нейросеть сгенерировала {len(neural_predictions)} предсказаний")
            except Exception as e:
                logger.error(f"❌ Ошибка нейросетевого предсказания: {e}")

        # 2. Статистические предсказания
        statistical_predictions = self._statistical_predictions(recent_numbers, top_k)
        statistical_predictions = [(group, score * 0.3, 'statistical') for group, score in statistical_predictions]
        all_predictions.extend(statistical_predictions)

        # 3. Случайные предсказания как fallback
        random_predictions = self._random_predictions(top_k)
        random_predictions = [(group, score * 0.1, 'random') for group, score in random_predictions]
        all_predictions.extend(random_predictions)

        # Объединяем и ранжируем предсказания
        final_predictions = self._merge_predictions(all_predictions)
        final_predictions.sort(key=lambda x: x[1], reverse=True)
        
        logger.info(f"🎯 Ансамбль сгенерировал {len(final_predictions)} финальных предсказаний")
        return final_predictions[:top_k]

    def _statistical_predictions(self, recent_numbers: List[int], top_k: int):
        """Статистические предсказания на основе частот чисел"""
        if len(recent_numbers) < 20:
            return []

        # Анализ частот чисел в последних группах
        freq = {}
        for num in recent_numbers[-40:]:  # Используем последние 40 чисел
            freq[num] = freq.get(num, 0) + 1

        # Нормализуем частоты
        total = sum(freq.values())
        if total == 0:
            return []

        predictions = []
        numbers = list(range(1, 27))
        
        for _ in range(top_k * 3):  # Генерируем больше кандидатов
            # Выбираем числа с учетом частот
            selected = []
            for pair in range(2):  # Две пары
                pair_numbers = []
                attempts = 0
                while len(pair_numbers) < 2 and attempts < 10:
                    num = random.choices(numbers, weights=[freq.get(n, 0.1) for n in numbers])[0]
                    if num not in pair_numbers:
                        pair_numbers.append(num)
                    attempts += 1
                
                pair_numbers.sort()
                selected.extend(pair_numbers)

            group = tuple(selected)
            
            # Рассчитываем score на основе частот
            score = sum(freq.get(num, 0) for num in group) / total
            predictions.append((group, score))

        # Фильтруем и сортируем
        predictions = [(group, score) for group, score in predictions if score > 0]
        predictions.sort(key=lambda x: x[1], reverse=True)
        return predictions[:top_k]

    def _random_predictions(self, top_k: int):
        """Случайные предсказания как fallback"""
        predictions = []
        for _ in range(top_k):
            group = (
                random.randint(1, 13), random.randint(1, 13),  # Первая пара
                random.randint(14, 26), random.randint(14, 26)  # Вторая пара
            )
            score = random.uniform(0.001, 0.01)
            predictions.append((group, score))
        return predictions

    def _merge_predictions(self, all_predictions):
        """Объединение предсказаний из разных источников"""
        merged = {}
        for group, score, source in all_predictions:
            if group in merged:
                # Если группа уже есть, увеличиваем оценку
                merged[group] += score
            else:
                merged[group] = score

        return [(group, score) for group, score in merged.items()]
