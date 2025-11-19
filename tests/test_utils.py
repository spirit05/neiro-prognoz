# tests/test_utils.py
"""
Утилиты для тестирования оркестратора
"""
import logging
from typing import Dict, Any
from ml.core.orchestrator import MLOrchestrator
from ml.core.config_loader import ConfigLoader

class TestOrchestrator(MLOrchestrator):
    __test__ = False
    """Оркестратор для тестирования с изолированным состоянием"""
    
    def __init__(self, config: Dict[str, Any] = None):
        super().__init__(config)
        self.test_mode = True

        # Отключаем автоматическую инициализацию для тестов
        self.config = config or {}
        self.logger = logging.getLogger(__name__)
        
        # Инициализируем только реестры
        self._models = {}
        self._feature_engineers = {}
        self._ensemble_predictors = {}
        self._model_registry = {}
        self._training_history = []
        self._prediction_stats = {}
        
        # Отключаем автоматическую загрузку конфигов
        self._config_loader = ConfigLoader()
        self.self_learning_system = None
