# /opt/dev/web/utils/data_helpers.py
import sys
import os
sys.path.append('/opt/dev')

from ml.core.predictor import EnhancedPredictor
from ml.learning.self_learning import SelfLearningSystem
from services.auto_learning.service import AutoLearningService

class WebDataManager:
    def __init__(self):
        self.ml_system = SelfLearningSystem()
        self.auto_service = AutoLearningService()
    
    def get_system_status(self):
        """Получить статус всей системы"""
        return {
            'ml_system': self.ml_system.get_training_status(),
            'auto_service': self.auto_service.get_service_status(),
            'predictions': self.get_recent_predictions()
        }