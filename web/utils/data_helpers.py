# /opt/dev/web/utils/data_helpers.py
"""
Помощники для работы с данными в веб-интерфейсе
"""
import json
import logging
from typing import List, Tuple, Dict, Any
from config.paths import DATASET_FILE, PREDICTIONS_STATE_FILE

logger = logging.getLogger(__name__)

def load_dataset() -> List[str]:
    """Загрузка датасета"""
    try:
        if DATASET_FILE.exists():
            with open(DATASET_FILE, 'r', encoding='utf-8') as f:
                return json.load(f)
        return []
    except Exception as e:
        logger.error(f"❌ Ошибка загрузки датасета: {e}")
        return []

def save_predictions(predictions: List[Tuple[Tuple[int, int, int, int], float]]):
    """Сохранение прогнозов"""
    try:
        predictions_data = {
            'timestamp': _get_timestamp(),
            'predictions': [
                {
                    'group': list(group),
                    'confidence': score,
                    'position': i + 1
                }
                for i, (group, score) in enumerate(predictions)
            ]
        }
        
        with open(PREDICTIONS_STATE_FILE, 'w', encoding='utf-8') as f:
            json.dump(predictions_data, f, ensure_ascii=False, indent=2)
        
        logger.info(f"💾 Сохранено {len(predictions)} прогнозов")
        
    except Exception as e:
        logger.error(f"❌ Ошибка сохранения прогнозов: {e}")

def load_predictions() -> List[Tuple[Tuple[int, int, int, int], float]]:
    """Загрузка сохраненных прогнозов"""
    try:
        if PREDICTIONS_STATE_FILE.exists():
            with open(PREDICTIONS_STATE_FILE, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            predictions = []
            for pred in data.get('predictions', []):
                group_tuple = tuple(pred['group'])
                confidence = pred['confidence']
                predictions.append((group_tuple, confidence))
            
            return predictions
        return []
    except Exception as e:
        logger.error(f"❌ Ошибка загрузки прогнозов: {e}")
        return []

def validate_group(combination: str) -> bool:
    """Валидация группы чисел"""
    try:
        numbers = [int(x) for x in combination.strip().split()]
        if len(numbers) != 4:
            return False
        if any(x < 1 or x > 26 for x in numbers):
            return False
        if len(set(numbers)) != 4:
            return False
        return True
    except:
        return False

def compare_groups(group1: Tuple[int, int, int, int], group2: Tuple[int, int, int, int]) -> Dict[str, int]:
    """Сравнение двух групп чисел"""
    matches = 0
    for num in group1:
        if num in group2:
            matches += 1
    
    return {
        'total_matches': matches,
        'first_pair_matches': len(set(group1[:2]) & set(group2[:2])),
        'second_pair_matches': len(set(group1[2:]) & set(group2[2:]))
    }

def _get_timestamp() -> str:
    """Получить timestamp"""
    from datetime import datetime
    return datetime.now().isoformat()