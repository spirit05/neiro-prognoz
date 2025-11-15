# /opt/model/ml/ensemble/combiners/weighted_combiner.py
"""
Weighted combiner - ЧИСТАЯ РЕАЛИЗАЦИЯ комбинирования предсказаний
"""

from typing import Dict, List, Any
from ml.core.types import PredictionResponse
import numpy as np


class WeightedCombiner:
    """Комбинатор с весами - ЧИСТАЯ РЕАЛИЗАЦИЯ"""
    
    def __init__(self, weights: Dict[str, float]):
        self.weights = weights
    
    def combine(self, predictions: Dict[str, PredictionResponse]) -> PredictionResponse:
        """Комбинирование предсказаний с весами"""
        if not predictions:
            return PredictionResponse(predictions=[], model_id="combined", inference_time=0.0)
        
        all_weighted = []
        
        for model_id, response in predictions.items():
            weight = self.weights.get(model_id, 1.0)
            
            for i, pred in enumerate(response.predictions):
                confidence = self._calculate_confidence(response, i, weight)
                all_weighted.append((pred, confidence, model_id))
        
        # Агрегация и сортировка
        aggregated = self._aggregate_predictions(all_weighted)
        
        return PredictionResponse(
            predictions=[pred for pred, _ in aggregated],
            model_id="combined",
            inference_time=sum(r.inference_time for r in predictions.values())
        )
    
    def _calculate_confidence(self, response: PredictionResponse, index: int, weight: float) -> float:
        """Расчет уверенности с учетом весов"""
        base_confidence = 1.0
        
        if response.probabilities and index < len(response.probabilities):
            probs = response.probabilities[index]
            if isinstance(probs, (list, np.ndarray)) and len(probs) > 0:
                base_confidence = float(np.max(probs))
        
        return base_confidence * weight
    
    def _aggregate_predictions(self, weighted_predictions: List[tuple]) -> List[tuple]:
        """Агрегация предсказаний по уникальным значениям"""
        aggregated = {}
        
        for pred, confidence, model_id in weighted_predictions:
            pred_key = tuple(pred) if isinstance(pred, (list, tuple)) else pred
            
            if pred_key in aggregated:
                aggregated[pred_key] += confidence
            else:
                aggregated[pred_key] = confidence
        
        return sorted(
            [(pred, score) for pred, score in aggregated.items()],
            key=lambda x: x[1],
            reverse=True
        )
