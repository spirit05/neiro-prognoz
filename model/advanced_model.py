# [file name]: model/advanced_model.py
"""
Продвинутая архитектура нейросети с дополнительными features
"""

import torch
import torch.nn as nn
import torch.nn.functional as F

class AdvancedSequencePredictor(nn.Module):
    def __init__(self, input_size: int = 150, hidden_size: int = 256):
        super().__init__()
        
        # Основные features (увеличенный input_size)
        self.main_network = nn.Sequential(
            nn.Linear(input_size, hidden_size),
            nn.ReLU(),
            nn.Dropout(0.3),
            nn.Linear(hidden_size, hidden_size),
            nn.ReLU(),
            nn.Dropout(0.3),
        )
        
        # Ветвь для временных паттернов
        self.temporal_branch = nn.Sequential(
            nn.Linear(50, hidden_size // 2),  # Временные features
            nn.ReLU(),
            nn.Linear(hidden_size // 2, hidden_size // 4),
        )
        
        # Ветвь для вероятностных features
        self.probabilistic_branch = nn.Sequential(
            nn.Linear(104, hidden_size // 2),  # 26 чисел × 4 позиции
            nn.ReLU(),
            nn.Linear(hidden_size // 2, hidden_size // 4),
        )
        
        # Объединение features
        combined_size = hidden_size + hidden_size // 4 + hidden_size // 4
        self.combiner = nn.Sequential(
            nn.Linear(combined_size, hidden_size),
            nn.ReLU(),
            nn.Dropout(0.2),
            nn.Linear(hidden_size, hidden_size // 2),
            nn.ReLU(),
        )
        
        # Отдельные выходные головки для каждой позиции
        self.output_heads = nn.ModuleList([
            nn.Sequential(
                nn.Linear(hidden_size // 2, 128),
                nn.ReLU(),
                nn.Linear(128, 26)
            ) for _ in range(4)
        ])
        
    def forward(self, x, temporal_features=None, probabilistic_features=None):
        # Основные features
        main_out = self.main_network(x)
        
        # Временные features (если предоставлены)
        temporal_out = torch.zeros(main_out.size(0), self.temporal_branch[-1].out_features).to(x.device)
        if temporal_features is not None:
            temporal_out = self.temporal_branch(temporal_features)
        
        # Вероятностные features (если предоставлены)
        probabilistic_out = torch.zeros(main_out.size(0), self.probabilistic_branch[-1].out_features).to(x.device)
        if probabilistic_features is not None:
            probabilistic_out = self.probabilistic_branch(probabilistic_features)
        
        # Объединение
        combined = torch.cat([main_out, temporal_out, probabilistic_out], dim=1)
        combined_out = self.combiner(combined)
        
        # Выходы для каждой позиции
        outputs = []
        for head in self.output_heads:
            outputs.append(head(combined_out))
        
        return torch.stack(outputs, dim=1)

# Совместимая версия для постепенного внедрения
class CompatibleEnhancedPredictor(nn.Module):
    """Совместимая версия с улучшенной архитектурой"""
    
    def __init__(self, input_size: int = 50, hidden_size: int = 256):
        super().__init__()
        
        # Используем улучшенную архитектуру но с совместимым интерфейсом
        self.advanced_model = AdvancedSequencePredictor(input_size, hidden_size)
        
    def forward(self, x):
        # Совместимый интерфейс - используем только основные features
        return self.advanced_model(x)