# model/simple_nn/model.py
"""
УСИЛЕННАЯ нейросеть для предсказания чисел 1-26
"""

import torch
import torch.nn as nn

class EnhancedNumberPredictor(nn.Module):
    def __init__(self, input_size: int = 50, hidden_size: int = 512):  # Увеличили hidden_size
        super(EnhancedNumberPredictor, self).__init__()
        
        # Усиленная архитектура с residual connections
        self.feature_extractor = nn.Sequential(
            nn.Linear(input_size, hidden_size),
            nn.ReLU(),
            nn.Dropout(0.3),
            
            nn.Linear(hidden_size, hidden_size),
            nn.ReLU(),
            nn.Dropout(0.3),
            
            nn.Linear(hidden_size, hidden_size // 2),
            nn.ReLU(),
            nn.Dropout(0.2),
        )
        
        # Отдельные головы для каждой позиции с разными весами
        self.head1 = nn.Sequential(
            nn.Linear(hidden_size // 2, 256),
            nn.ReLU(),
            nn.Dropout(0.2),
            nn.Linear(256, 128),
            nn.ReLU(),
            nn.Linear(128, 26)
        )
        
        self.head2 = nn.Sequential(
            nn.Linear(hidden_size // 2, 256),
            nn.ReLU(),
            nn.Dropout(0.2),
            nn.Linear(256, 128),
            nn.ReLU(),
            nn.Linear(128, 26)
        )
        
        self.head3 = nn.Sequential(
            nn.Linear(hidden_size // 2, 256),
            nn.ReLU(),
            nn.Dropout(0.2),
            nn.Linear(256, 128),
            nn.ReLU(),
            nn.Linear(128, 26)
        )
        
        self.head4 = nn.Sequential(
            nn.Linear(hidden_size // 2, 256),
            nn.ReLU(),
            nn.Dropout(0.2),
            nn.Linear(256, 128),
            nn.ReLU(),
            nn.Linear(128, 26)
        )
    
    def forward(self, x):
        features = self.feature_extractor(x)
        
        out1 = self.head1(features)
        out2 = self.head2(features)
        out3 = self.head3(features)
        out4 = self.head4(features)
        
        # Возвращаем тензор размерности [batch_size, 4, 26]
        return torch.stack([out1, out2, out3, out4], dim=1)