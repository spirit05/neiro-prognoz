# /opt/project/model/simple_nn/predictor_fast.py
import torch
import numpy as np
from typing import List, Tuple
import os
import random

from .model import EnhancedNumberPredictor
from .features import FeatureExtractor

class FastPredictor:
    def __init__(self, model_path: str = "data/simple_model.pth"):
        self.model_path = model_path
        self.model = None
        self.feature_extractor = FeatureExtractor(history_size=25)
        self.is_trained = False
    
    def load_model(self) -> bool:
        if not os.path.exists(self.model_path):
            return False
        try:
            checkpoint = torch.load(self.model_path, map_location='cpu')
            config = checkpoint['model_config']
            self.model = EnhancedNumberPredictor(input_size=config['input_size'], hidden_size=config['hidden_size'])
            self.model.load_state_dict(checkpoint['model_state_dict'])
            self.model.eval()
            self.is_trained = True
            return True
        except:
            return False
    
    def predict_group(self, number_history: List[int], top_k: int = 4) -> List[Tuple[Tuple[int, int, int, int], float]]:
        """СУПЕР-ПРОСТОЙ предсказатель"""
        if not self.is_trained:
            if not self.load_model():
                return []
        
        if len(number_history) < 25:
            return []
        
        # ТОЛЬКО базовые features
        features = self.feature_extractor.extract_features(number_history[-25:])
        features_tensor = torch.tensor(features, dtype=torch.float32).unsqueeze(0)
        
        with torch.no_grad():
            outputs = self.model(features_tensor)
            probabilities = torch.softmax(outputs, dim=-1)
            
            # ПРОСТЕЙШАЯ логика - топ-1 число для каждой позиции
            result = []
            for pos in range(4):
                probs = probabilities[0][pos]
                top_prob, top_idx = torch.topk(probs, 1)
                number = top_idx.item() + 1
                confidence = top_prob.item()
                result.append((number, confidence))
            
            # Создаем 4 варианта на основе топ чисел
            base_numbers = [r[0] for r in result]
            base_confidence = np.prod([r[1] for r in result])
            
            candidates = []
            
            # 1. Базовый вариант
            candidates.append((tuple(base_numbers), base_confidence))
            
            # 2-4. Простые вариации
            for i in range(3):
                variant = base_numbers.copy()
                # Меняем одно число
                change_idx = random.randint(0, 3)
                available_nums = [n for n in range(1, 27) if n not in variant]
                if available_nums:
                    variant[change_idx] = random.choice(available_nums)
                
                # Проверяем пары
                if change_idx in [0, 1] and variant[0] == variant[1]:
                    variant[1] = random.choice([n for n in range(1, 27) if n != variant[0]])
                elif change_idx in [2, 3] and variant[2] == variant[3]:
                    variant[3] = random.choice([n for n in range(1, 27) if n != variant[2]])
                
                candidates.append((tuple(variant), base_confidence * 0.5))
            
            return candidates