# [file name]: ml/core/model.py
"""
Упрощенная нейросеть для предсказания чисел 1-26 - как в старой архитектуре
"""

import torch
import torch.nn as nn

class EnhancedNumberPredictor(nn.Module):
    def __init__(self, input_size: int = 50, hidden_size: int = 128):  # Уменьшил hidden_size
        super(EnhancedNumberPredictor, self).__init__()
        
        # 🔧 УПРОЩЕНИЕ: Используем простую архитектуру как в старой версии
        self.network = nn.Sequential(
            nn.Linear(input_size, hidden_size),
            nn.ReLU(),
            nn.Dropout(0.2),
            
            nn.Linear(hidden_size, hidden_size),
            nn.ReLU(), 
            nn.Dropout(0.2),
            
            nn.Linear(hidden_size, 4 * 26)  # 4 позиции × 26 чисел
        )
        
        self.input_size = input_size
        self.hidden_size = hidden_size
    
    def forward(self, x):
        # 🔧 ИСПРАВЛЕНИЕ: Простой forward как в старой архитектуре
        output = self.network(x)
        # Преобразуем в [batch_size, 4, 26]
        return output.view(-1, 4, 26)
