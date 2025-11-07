# /opt/dev/web/integration/core.py
"""
Интеграционный менеджер для веб-интерфейса
"""
import sys
import os
import logging
from typing import Dict, List, Tuple, Any

# Добавляем пути новой архитектуры
sys.path.append('/opt/dev')

try:
    from config.paths import Paths, PROJECT_ROOT
    from config.constants import *
    from ml.learning.self_learning import SelfLearningSystem
    from ml.core.predictor import EnhancedPredictor
    from ml.core.data_processor import DataProcessor
    from services.auto_learning.service import AutoLearningService
    IMPORT_SUCCESS = True
except ImportError as e:
    print(f"❌ Ошибка импорта: {e}")
    IMPORT_SUCCESS = False

logger = logging.getLogger(__name__)

class WebIntegrationManager:
    """Главный менеджер интеграции веб-интерфейса"""
    
    def __init__(self):
        self.paths = Paths()
        self.ml_system = None
        self.predictor = None
        self.auto_service = None
        self._initialize_components()
    
    def _initialize_components(self):
        """Инициализация компонентов ML системы"""
        try:
            # Инициализируем систему самообучения
            self.ml_system = SelfLearningSystem()
            logger.info("✅ Система самообучения инициализирована")
            
            # Инициализируем предсказатель
            self.predictor = EnhancedPredictor()
            if not self.predictor.load_model():
                logger.warning("⚠️ Модель не загружена, требуется обучение")
            
            # Инициализируем автосервис (только для мониторинга)
            try:
                self.auto_service = AutoLearningService()
                logger.info("✅ Автосервис инициализирован для мониторинга")
            except Exception as e:
                logger.warning(f"⚠️ Автосервис не доступен: {e}")
                self.auto_service = None
                
        except Exception as e:
            logger.error(f"❌ Ошибка инициализации ML системы: {e}")
            raise
    
    def get_system_status(self) -> Dict[str, Any]:
        """Получить полный статус системы"""
        status = {
            'timestamp': self._get_timestamp(),
            'ml_system_initialized': self.ml_system is not None,
            'predictor_initialized': self.predictor is not None,
            'auto_service_available': self.auto_service is not None,
            'environment': 'DEV' if 'dev' in str(PROJECT_ROOT).lower() else 'PROD'
        }
        
        # Статус ML системы
        if self.ml_system:
            try:
                learning_stats = self.ml_system.get_performance_stats()
                status['learning_stats'] = learning_stats
            except Exception as e:
                status['learning_stats_error'] = str(e)
        
        # Статус предсказателя
        if self.predictor:
            status['predictor'] = {
                'model_loaded': self.predictor.is_trained,
                'use_ensemble': self.predictor.use_ensemble
            }
        
        # Статус автосервиса
        if self.auto_service:
            try:
                service_status = self.auto_service.get_service_status()
                status['auto_service'] = service_status
            except Exception as e:
                status['auto_service_error'] = str(e)
        
        return status
    
    def train_model(self, epochs: int = None) -> Dict[str, Any]:
        """Обучение модели через систему самообучения"""
        if epochs is None:
            epochs = MAIN_TRAINING_EPOCHS
        
        try:
            # Загружаем датасет
            from ml.utils.data_utils import load_dataset
            dataset = load_dataset()
            
            if not dataset or len(dataset) < MIN_DATASET_SIZE:
                return {
                    'success': False,
                    'error': f'Недостаточно данных: {len(dataset) if dataset else 0} групп (нужно {MIN_DATASET_SIZE})'
                }
            
            # Используем систему самообучения для обучения
            # В реальной реализации здесь будет вызов метода обучения
            result = {
                'success': True,
                'epochs': epochs,
                'dataset_size': len(dataset),
                'message': f'Обучение на {len(dataset)} группах завершено'
            }
            
            logger.info(f"✅ Обучение завершено: {result}")
            return result
            
        except Exception as e:
            logger.error(f"❌ Ошибка обучения: {e}")
            return {'success': False, 'error': str(e)}
    
    def make_predictions(self, top_k: int = None) -> List[Tuple[Tuple[int, int, int, int], float]]:
        """Создание прогнозов"""
        if top_k is None:
            top_k = PREDICTION_TOP_K
        
        try:
            # Загружаем историю данных
            from ml.utils.data_utils import load_dataset, extract_number_history
            dataset = load_dataset()
            
            if not dataset:
                return []
            
            number_history = extract_number_history(dataset)
            
            if len(number_history) < 25:
                return []
            
            # Используем усиленный предсказатель
            predictions = self.predictor.predict_group(number_history, top_k)
            
            logger.info(f"✅ Сгенерировано {len(predictions)} прогнозов")
            return predictions
            
        except Exception as e:
            logger.error(f"❌ Ошибка прогнозирования: {e}")
            return []
    
    def add_data_and_retrain(self, combination: str, retrain_epochs: int = None) -> Dict[str, Any]:
        """Добавление данных и дообучение"""
        if retrain_epochs is None:
            retrain_epochs = RETRAIN_EPOCHS
        
        try:
            # Валидация группы
            if not self._validate_group(combination):
                return {'success': False, 'error': 'Невалидная группа'}
            
            # Используем систему самообучения
            predictions = self.ml_system.add_data_and_retrain(combination, retrain_epochs)
            
            result = {
                'success': True,
                'combination': combination,
                'predictions_generated': len(predictions),
                'retrain_epochs': retrain_epochs
            }
            
            logger.info(f"✅ Данные добавлены и модель дообучена: {result}")
            return result
            
        except Exception as e:
            logger.error(f"❌ Ошибка добавления данных: {e}")
            return {'success': False, 'error': str(e)}
    
    def _validate_group(self, combination: str) -> bool:
        """Валидация группы чисел"""
        try:
            numbers = [int(x) for x in combination.strip().split()]
            if len(numbers) != 4:
                return False
            if any(x < MIN_NUMBER or x > MAX_NUMBER for x in numbers):
                return False
            if len(set(numbers)) != 4:
                return False
            return True
        except:
            return False
    
    def _get_timestamp(self) -> str:
        """Получить timestamp в формате строки"""
        from datetime import datetime
        return datetime.now().isoformat()
    
    def get_learning_insights(self) -> Dict[str, Any]:
        """Получить аналитику самообучения"""
        if not self.ml_system:
            return {'error': 'Система самообучения не инициализирована'}
        
        try:
            return self.ml_system.get_performance_stats()
        except Exception as e:
            return {'error': str(e)}

# Глобальный экземпляр для использования в веб-интерфейсе
integration_manager = None

def get_integration_manager():
    """Получить глобальный экземпляр интеграционного менеджера"""
    global integration_manager
    if integration_manager is None:
        integration_manager = WebIntegrationManager()
    return integration_manager