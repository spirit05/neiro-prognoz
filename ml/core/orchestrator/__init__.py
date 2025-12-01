# [file name]: ml/core/orchestrator/__init__.py
"""
Фасад MLOrchestrator - основной интерфейс системы
СОХРАНЯЕТ ПОЛНУЮ ОБРАТНУЮ СОВМЕСТИМОСТЬ
ИСПРАВЛЕННАЯ ВЕРСИЯ ДЛЯ РЕГИСТРАЦИИ МОДЕЛЕЙ
"""

from .base_orchestrator import BaseOrchestrator
from .managers.model_manager import ModelManager
from .managers.data_manager import DataManager
from .managers.workflow_manager import WorkflowManager
from .managers.notification_manager import NotificationManager
from .managers.api_manager import ApiManager

from ml.core.types import (
    ModelType, ModelStatus, TrainingConfig, ModelMetadata,
    TrainingResult, PredictionResponse, DataBatch, FeatureSpec,
    PredictionRequest, DataType, AnalysisResult, LearningHistory
)


class MLOrchestrator(BaseOrchestrator):
    """
    Основной фасад оркестратора - делегирует операции менеджерам
    СОХРАНЯЕТ ПОЛНУЮ ОБРАТНУЮ СОВМЕСТИМОСТЬ С СУЩЕСТВУЮЩИМ API
    ИСПРАВЛЕННАЯ ВЕРСИЯ ДЛЯ РЕГИСТРАЦИИ МОДЕЛЕЙ
    """
    
    def __init__(self, config: dict = None):
        super().__init__(config)
        
        # 🔧 ИСПРАВЛЕНИЕ: Регистрируем модели по умолчанию напрямую (до менеджеров)
        self._register_default_models_direct()
        
        # Инициализация менеджеров
        self.model_manager = ModelManager(self)
        self.data_manager = DataManager(self) 
        self.workflow_manager = WorkflowManager(self)
        self.notification_manager = NotificationManager(self)
        self.api_manager = ApiManager(self)
        
        # 🔧 ИСПРАВЛЕНИЕ: Синхронизируем менеджеры с уже зарегистрированными моделями
        self._sync_managers_with_registry()
        
        self.logger.info("✅ Модульный MLOrchestrator инициализирован")
    
    def _register_default_models_direct(self) -> None:
        """Прямая регистрация моделей по умолчанию для системы"""
        try:
            from ml.models.base import EnhancedPredictor
            
            # 🔧 ИСПРАВЛЕНИЕ: Создаем модель с адаптивным input_size
            # Начальное значение 65 соответствует текущему DataProcessor
            enhanced_model = EnhancedPredictor(
                model_id="enhanced_predictor_v2", 
                input_size=65  # 🔧 ИЗМЕНЕНО: 65 вместо 50
            )
            self.register_model_direct(enhanced_model)
            
            self.logger.info("✅ Модели по умолчанию зарегистрированы напрямую в MLOrchestrator")
            
        except Exception as e:
            self.logger.error(f"❌ Ошибка прямой регистрации моделей по умолчанию: {e}")

    def _sync_managers_with_registry(self) -> None:
        """Синхронизация менеджеров с уже зарегистрированными моделями"""
        try:
            # Передаем информацию о зарегистрированных моделях в model_manager
            for model_id, model in self.models.items():
                if hasattr(self.model_manager, '_sync_model_registry'):
                    self.model_manager._sync_model_registry(model_id, model)
            
            self.logger.info(f"✅ Менеджеры синхронизированы с {len(self.models)} моделями")
            
        except Exception as e:
            self.logger.error(f"❌ Ошибка синхронизации менеджеров: {e}")
    
    # ========== ФАСАДНЫЕ МЕТОДЫ - ДЕЛЕГИРУЮТ МЕНЕДЖЕРАМ ==========
    
    def register_model(self, model):
        """Регистрация модели - делегирует ModelManager"""
        return self.model_manager.register_model(model)
    
    def train_model(self, model_id: str, data: DataBatch, config: TrainingConfig) -> TrainingResult:
        """Обучение модели - делегирует ModelManager"""
        return self.model_manager.train_model(model_id, data, config)

    def train_model_with_strategy(self, model_id: str, strategy_id: str, data: DataBatch, config: TrainingConfig) -> TrainingResult:
        """Обучение модели с указанной стратегией - делегирует ModelManager"""
        return self.model_manager.train_model_with_strategy(model_id, strategy_id, data, config)

    def clear_registry(self) -> None:
        """Очистка реестра моделей (для тестирования)"""
        return self.model_manager.clear_registry()
    
    def predict(self, request: PredictionRequest) -> PredictionResponse:
        """Предсказание - делегирует ModelManager"""
        return self.model_manager.predict(request)
    
    def prepare_training_data(self):
        """Подготовка данных - делегирует DataManager"""
        return self.data_manager.prepare_training_data()
    
    def create_prediction_features(self, recent_groups):
        """Создание фич - делегирует DataManager"""
        return self.data_manager.create_prediction_features(recent_groups)
    
    def add_new_data(self, new_groups):
        """Добавление данных - делегирует DataManager"""
        return self.data_manager.add_new_data(new_groups)
    
    # ========== WORKFLOW МЕТОДЫ - ДЕЛЕГИРУЮТ WorkflowManager ==========
    
    def workflow_add_single_group(self, group):
        """Workflow добавления одной группы"""
        return self.workflow_manager.workflow_add_single_group(group)
    
    def workflow_add_multiple_groups(self, groups, strategy="full_retrain"):
        """Workflow добавления нескольких групп"""
        return self.workflow_manager.workflow_add_multiple_groups(groups, strategy)
    
    def workflow_full_training_cycle(self):
        """Workflow полного цикла обучения"""
        self.logger.info("🎯 ВЫЗВАН: MLOrchestrator.workflow_full_training_cycle()")
        self.logger.info(f"🎯 Models в оркестраторе: {list(self.models.keys())}")
        if 'enhanced_predictor_v2' in self.models:
            model = self.models['enhanced_predictor_v2']
            self.logger.info(f"🎯 Модель enhanced_predictor_v2 обучена: {model.is_trained}")
        else:
            self.logger.error("❌ МОДЕЛЬ enhanced_predictor_v2 НЕ НАЙДЕНА")
        
        return self.workflow_manager.workflow_full_training_cycle()
    
    def workflow_generate_predictions(self):
        """Workflow генерации прогнозов"""
        return self.workflow_manager.workflow_generate_predictions()
    
    def get_system_overview(self):
        """Комплексный обзор системы"""
        return self.workflow_manager.get_system_overview()
    
    def get_learning_analytics(self):
        """Аналитика обучения"""
        return self.workflow_manager.get_learning_analytics()
    
    # ========== СОВМЕСТИМОСТЬ - СТАРЫЕ МЕТОДЫ ЧЕРЕЗ ФАСАД ==========
    
    def get_model_info(self, model_id):
        return self.model_manager.get_model_info(model_id)
    
    def list_models(self):
        return self.model_manager.list_models()
    
    def save_model(self, model_id, path):
        return self.model_manager.save_model(model_id, path)
    
    def load_model(self, model_id, path, model_class):
        return self.model_manager.load_model(model_id, path, model_class)
    
    def get_feature_engineers(self):
        return self.model_manager.get_feature_engineers()
    
    def extract_features(self, data, engineer_names=None):
        return self.model_manager.extract_features(data, engineer_names)
    
    def get_ensemble_predictors(self):
        return self.model_manager.get_ensemble_predictors()
    
    def ensemble_predict(self, history, top_k=15):
        return self.model_manager.ensemble_predict(history, top_k)
    
    def get_system_status(self):
        return self.workflow_manager.get_system_status()
    
    def setup_self_learning(self, config=None):
        return self.model_manager.setup_self_learning(config)
    
    def analyze_predictions(self, predictions, actual_results):
        return self.model_manager.analyze_predictions(predictions, actual_results)
    
    def get_learning_recommendations(self):
        return self.model_manager.get_learning_recommendations()
    
    def get_performance_stats(self):
        return self.model_manager.get_performance_stats()
    
    def adjust_ensemble_weights(self, analysis_result):
        return self.model_manager.adjust_ensemble_weights(analysis_result)
    
    def check_component_integration(self):
        return self.model_manager.check_component_integration()
    
    def validate_prediction_accuracy(self, predictions, actuals):
        return self.data_manager.validate_prediction_accuracy(predictions, actuals)
    
    def backup_dataset(self):
        return self.data_manager.backup_dataset()
    
    def get_data_processing_info(self):
        return self.data_manager.get_data_processing_info()


# Сохраняем обратную совместимость - старый импорт
__all__ = ['MLOrchestrator']
