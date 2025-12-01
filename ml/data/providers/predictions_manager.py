# [file name]: ml/data/providers/predictions_manager.py
"""
PredictionsManager - управление сохранением и загрузкой прогнозов
ИСПРАВЛЕННАЯ ВЕРСИЯ
"""

import json
import logging
from typing import List, Tuple, Any, Dict
from pathlib import Path
from datetime import datetime


class PredictionsManager:
    """Менеджер для работы с прогнозами"""

    def __init__(self, predictions_path: str = None):
        self.predictions_path = predictions_path or "data/predictions.json"
        self.logger = logging.getLogger(__name__)
        
        # Создаем директорию если не существует
        Path(self.predictions_path).parent.mkdir(parents=True, exist_ok=True)
        
        self.logger.info(f"✅ PredictionsManager инициализирован с путем: {self.predictions_path}")

    def save_predictions(self, predictions: List[Tuple[Tuple[int, int, int, int], float]]) -> bool:
        """Сохранение прогнозов в файл"""
        try:
            # 🔧 ИСПРАВЛЕНИЕ: Правильная сериализация прогнозов
            serializable_predictions = []
            
            for group, score in predictions:
                # Преобразуем кортеж в список для JSON сериализации
                group_list = list(group) if isinstance(group, tuple) else group
                
                # Проверяем валидность группы
                if self._is_valid_prediction(group_list):
                    serializable_predictions.append({
                        "group": group_list,
                        "score": float(score),
                        "timestamp": datetime.now().isoformat()
                    })
                else:
                    self.logger.warning(f"⚠️ Пропущен невалидный прогноз: {group_list}")

            data = {
                "predictions": serializable_predictions,
                "total_count": len(serializable_predictions),
                "last_updated": datetime.now().isoformat()
            }

            with open(self.predictions_path, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2, ensure_ascii=False)

            self.logger.info(f"✅ Сохранено {len(serializable_predictions)} прогнозов")
            return True

        except Exception as e:
            self.logger.error(f"❌ Ошибка сохранения прогнозов: {e}")
            return False

    def load_predictions(self) -> List[Tuple[Tuple[int, int, int, int], float]]:
        """Загрузка прогнозов из файла"""
        try:
            if not Path(self.predictions_path).exists():
                self.logger.info("📭 Файл прогнозов не существует")
                return []

            with open(self.predictions_path, 'r', encoding='utf-8') as f:
                data = json.load(f)

            predictions = []
            for item in data.get("predictions", []):
                group_tuple = tuple(item["group"])
                score = item["score"]
                predictions.append((group_tuple, score))

            self.logger.info(f"✅ Загружено {len(predictions)} прогнозов")
            return predictions

        except Exception as e:
            self.logger.error(f"❌ Ошибка загрузки прогнозов: {e}")
            return []

    def get_recent_predictions(self, count: int = 10) -> List[Tuple[Tuple[int, int, int, int], float]]:
        """Получение последних прогнозов"""
        all_predictions = self.load_predictions()
        return all_predictions[:count]

    def clear_predictions(self) -> bool:
        """Очистка всех прогнозов"""
        try:
            if Path(self.predictions_path).exists():
                Path(self.predictions_path).unlink()
                self.logger.info("✅ Прогнозы очищены")
            return True
        except Exception as e:
            self.logger.error(f"❌ Ошибка очистки прогнозов: {e}")
            return False

    def _is_valid_prediction(self, group: List[int]) -> bool:
        """Проверка валидности группы прогноза"""
        try:
            if not isinstance(group, list) or len(group) != 4:
                return False
            
            # Проверяем что все числа в допустимом диапазоне
            if not all(1 <= x <= 26 for x in group):
                return False
                
            return True
        except:
            return False
