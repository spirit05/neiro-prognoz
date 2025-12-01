#/opt/model/services/telegram/ml_dispatcher.py
"""
MLDispatcher - тонкая прослойка между Telegram ботом и WorkflowManager
Аналогичен MLIntegration из веб-интерфейса
"""

import os
import sys
import logging
from typing import Dict, Any, List, Optional, Tuple
from pathlib import Path

# 🔧 ПРАВИЛЬНЫЙ ПУТЬ К ПРОЕКТУ
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

from ml.core.orchestrator import MLOrchestrator
from ml.core.orchestrator.types import WorkflowResult, SystemOverview, LearningAnalytics
from ml.data.providers.dataset_manager import DatasetManager
from ml.data.providers.predictions_manager import PredictionsManager


class MLDispatcher:
    """
    Диспетчер для Telegram бота - предоставляет упрощенный интерфейс к WorkflowManager
    """
    
    def __init__(self, config_path: str = None):
        self.project_root = project_root
        self.orchestrator = None
        self.is_initialized = False
        
        # 🔧 ПРАВИЛЬНЫЙ ПУТЬ К КОНФИГУ
        if config_path:
            self.config_path = Path(config_path)
        else:
            self.config_path = self.project_root / 'config' / 'orchestrator_config.yaml'
            
        self.logger = logging.getLogger('telegram_bot.ml_dispatcher')
        self.logger.info(f"📁 Project root: {self.project_root}")
        self.logger.info(f"📁 Config path: {self.config_path}")
    
    def initialize(self) -> bool:
        """Инициализация ML системы (аналогично MLIntegration)"""
        try:
            self.logger.info("🔄 Инициализация ML системы для Telegram бота...")
            
            # Загружаем конфигурацию
            config = self._load_config()
            
            # Создаем оркестратор
            self.orchestrator = MLOrchestrator(config)
            
            # 🔧 НЕ ПЕРЕЗАПИСЫВАЕМ МОДЕЛЬ, если она уже есть
            # Оркестратор уже зарегистрировал модель по умолчанию
            self.logger.info(f"✅ Зарегистрированные модели: {list(self.orchestrator.models.keys())}")
            
            # Проверяем, есть ли сохраненная модель, и пытаемся ее загрузить
            # НО НЕ ПЕРЕЗАПИСЫВАЕМ существующую
            model_loaded = self._try_load_saved_model_safely()
            
            # 🔧 НЕ СОЗДАЕМ ПУСТЫЕ ДАТАСЕТЫ!
            # Просто проверяем существование необходимых директорий
            self._ensure_directories()
            
            self.is_initialized = True
            self.logger.info("✅ ML система успешно инициализирована для Telegram бота")
            return True
            
        except Exception as e:
            self.logger.error(f"❌ Ошибка инициализации ML системы: {e}")
            self.is_initialized = False
            return False
    
    def _try_load_saved_model_safely(self) -> bool:
        """Безопасная попытка загрузить сохраненную модель (без перезаписи)"""
        try:
            model_path = self.project_root / 'data' / 'models' / 'enhanced_predictor_v2.pth'
            
            if not model_path.exists():
                self.logger.info("📭 Файл модели не найден, используем модель по умолчанию")
                return False
            
            self.logger.info(f"🔍 Найден файл модели: {model_path}")
            
            # 🔧 ПРОВЕРЯЕМ, УЖЕ ЛИ ЗАРЕГИСТРИРОВАНА МОДЕЛЬ
            if "enhanced_predictor_v2" in self.orchestrator.models:
                existing_model = self.orchestrator.models["enhanced_predictor_v2"]
                
                # Если модель уже зарегистрирована, но не обучена - загружаем из файла
                if not existing_model.is_trained:
                    self.logger.info("🔄 Модель зарегистрирована, но не обучена, загружаем из файла...")
                    from ml.models.base import EnhancedPredictor
                    
                    success = self.orchestrator.model_manager.load_model(
                        "enhanced_predictor_v2", 
                        str(model_path), 
                        EnhancedPredictor
                    )
                    
                    if success:
                        self.logger.info("✅ Модель загружена из файла")
                        return True
                    else:
                        self.logger.warning("⚠️ Не удалось загрузить модель из файла")
                        return False
                else:
                    self.logger.info("✅ Модель уже зарегистрирована и обучена, пропускаем загрузку")
                    return True
            else:
                # Если модель не зарегистрирована, загружаем
                from ml.models.base import EnhancedPredictor
                
                success = self.orchestrator.model_manager.load_model(
                    "enhanced_predictor_v2", 
                    str(model_path), 
                    EnhancedPredictor
                )
                
                if success:
                    self.logger.info("✅ Модель загружена из файла")
                    return True
                else:
                    self.logger.warning("⚠️ Не удалось загрузить модель из файла")
                    return False
                
        except Exception as e:
            self.logger.error(f"❌ Ошибка при попытке загрузить модель: {e}")
            return False
    
    def _load_config(self) -> Dict[str, Any]:
        """Загрузка конфигурации"""
        try:
            import yaml
            
            # 🔧 ПРАВИЛЬНЫЙ ПУТЬ
            if not self.config_path.exists():
                self.logger.warning(f"⚠️ Файл конфигурации не найден: {self.config_path}")
                return {}
            
            with open(self.config_path, 'r', encoding='utf-8') as f:
                config = yaml.safe_load(f)
                
            self.logger.info(f"✅ Конфигурация загружена из {self.config_path}")
            return config
            
        except Exception as e:
            self.logger.error(f"❌ Ошибка загрузки конфигурации: {e}")
            return {}
    
    def _ensure_directories(self):
        """Проверяем существование необходимых директорий - НЕ СОЗДАЕМ ФАЙЛЫ!"""
        try:
            directories = [
                self.project_root / 'data' / 'models',
                self.project_root / 'data' / 'datasets', 
                self.project_root / 'data' / 'logs',
            ]
            
            for directory in directories:
                directory.mkdir(parents=True, exist_ok=True)
                self.logger.debug(f"📁 Проверена директория: {directory}")
            
        except Exception as e:
            self.logger.warning(f"⚠️ Ошибка при проверке директорий: {e}")
   
    def get_system_status(self) -> Dict[str, Any]:
        """Получение статуса системы - ИСПРАВЛЕННАЯ ВЕРСИЯ"""
        if not self.is_initialized or not self.orchestrator:
            return {
                'is_initialized': False,
                'is_trained': False,
                'dataset_size': 0,
                'has_sufficient_data': False,
                'architecture': 'НОВАЯ МОДУЛЬНАЯ',
                'model_type': 'УСИЛЕННАЯ НЕЙРОСЕТЬ',
                'model_loaded': False,
                'error': 'ML система не инициализирована'
            }
        
        try:
            # 🔧 ПРАВИЛЬНАЯ ПРОВЕРКА МОДЕЛИ
            model_trained = False
            model_loaded = False
            
            if "enhanced_predictor_v2" in self.orchestrator.models:
                model = self.orchestrator.models["enhanced_predictor_v2"]
                model_trained = model.is_trained
                model_loaded = True
                self.logger.info(f"🔍 Модель найдена, is_trained={model_trained}")
            
            # 🔧 ПРАВИЛЬНОЕ ПОЛУЧЕНИЕ ДАННЫХ
            dataset_size = 0
            try:
                dataset_manager = DatasetManager()
                dataset = dataset_manager.load_dataset()
                if isinstance(dataset, list):
                    dataset_size = len(dataset)
                elif hasattr(dataset, '__len__'):
                    dataset_size = len(dataset)
                self.logger.info(f"📊 Размер датасета: {dataset_size}")
            except Exception as e:
                self.logger.warning(f"⚠️ Не удалось загрузить датасет: {e}")
            
            # 🔧 ПРАВИЛЬНОЕ ПОЛУЧЕНИЕ ПРОГНОЗОВ
            predictions_count = 0
            try:
                predictions_manager = PredictionsManager()
                predictions = predictions_manager.load_predictions()
                
                # 🔧 ИСПРАВЛЕНИЕ: Правильная обработка формата прогнозов
                # PredictionsManager возвращает список кортежей (group, score)
                if isinstance(predictions, list):
                    predictions_count = len(predictions)
                elif isinstance(predictions, dict) and 'predictions' in predictions:
                    predictions_count = len(predictions['predictions'])
                    
            except Exception as e:
                self.logger.warning(f"⚠️ Не удалось загрузить прогнозы: {e}")
            
            return {
                'is_initialized': True,
                'is_trained': model_trained,
                'dataset_size': dataset_size,
                'has_sufficient_data': dataset_size >= 50,
                'architecture': 'НОВАЯ МОДУЛЬНАЯ',
                'model_type': 'УСИЛЕННАЯ НЕЙРОСЕТЬ',
                'model_loaded': model_loaded,
                'registered_models': list(self.orchestrator.models.keys()),
                'predictions_count': predictions_count,
                'data_status': 'sufficient' if dataset_size >= 50 else 'insufficient'
            }
        except Exception as e:
            self.logger.error(f"❌ Ошибка получения статуса системы: {e}")
            return {
                'is_initialized': True,
                'is_trained': False,
                'dataset_size': 0,
                'has_sufficient_data': False,
                'architecture': 'НОВАЯ МОДУЛЬНАЯ',
                'model_type': 'УСИЛЕННАЯ НЕЙРОСЕТЬ',
                'model_loaded': False,
                'error': str(e)
            }
    
    def get_predictions(self) -> Dict[str, Any]:
        """Получение сохраненных прогнозов - ИСПРАВЛЕННАЯ ВЕРСИЯ"""
        try:
            predictions_manager = PredictionsManager()
            predictions = predictions_manager.load_predictions()
            
            if not predictions:
                return {'success': False, 'message': 'Прогнозы не найдены', 'predictions': []}
            
            # 🔧 ИСПРАВЛЕНИЕ: Правильная обработка формата прогнозов
            # PredictionsManager возвращает список кортежей (group, score)
            if isinstance(predictions, list):
                # Преобразуем кортежи в словари для совместимости
                pred_list = []
                for pred in predictions:
                    if isinstance(pred, tuple) and len(pred) == 2:
                        group, score = pred
                        pred_list.append({
                            'group': list(group) if isinstance(group, tuple) else group,
                            'score': float(score) if score else 0.0,
                            'timestamp': None  # Указываем None, так как в кортеже нет timestamp
                        })
                
                return {
                    'success': True,
                    'message': f'Найдено {len(pred_list)} прогнозов',
                    'predictions': pred_list[:10],
                    'total_count': len(pred_list)
                }
            elif isinstance(predictions, dict):
                # Если это словарь с ключом 'predictions'
                pred_list = predictions.get('predictions', [])
                return {
                    'success': True,
                    'message': f'Найдено {len(pred_list)} прогнозов',
                    'predictions': pred_list[:10],
                    'total_count': len(pred_list),
                    'last_updated': predictions.get('last_updated')
                }
            else:
                return {'success': False, 'message': 'Неизвестный формат прогнозов', 'predictions': []}
                
        except Exception as e:
            self.logger.error(f"❌ Ошибка получения прогнозов: {e}")
            return {'success': False, 'message': f'Ошибка получения прогнозов: {str(e)}', 'predictions': []}
    
    def get_dataset_info(self) -> Dict[str, Any]:
        """Получение информации о датасете - ИСПРАВЛЕННАЯ ВЕРСИЯ"""
        try:
            dataset_manager = DatasetManager()
            dataset = dataset_manager.load_dataset()
            
            if dataset is None:
                dataset = []
            
            # Убедимся, что это список
            if not isinstance(dataset, list):
                dataset = []
            
            return {
                'success': True,
                'dataset_size': len(dataset),
                'valid_groups': len(dataset),  # Упрощенно, можно добавить валидацию
                'total_groups': len(dataset),
                'has_sufficient_data': len(dataset) >= 50,
                'message': f'Датасет содержит {len(dataset)} групп'
            }
        except Exception as e:
            self.logger.error(f"❌ Ошибка получения информации о датасете: {e}")
            return {'success': False, 'message': f'Ошибка получения информации о датасете: {str(e)}'}
    
    def add_single_group(self, group: List[int]) -> Dict[str, Any]:
        """Добавление одной группы через WorkflowManager"""
        if not self.is_initialized or not self.orchestrator:
            return {'success': False, 'message': 'Система не инициализирована'}
        
        try:
            self.logger.info(f"🎯 Добавление одной группы через Telegram бота: {group}")
            result = self.orchestrator.workflow_add_single_group(group)
            
            return {
                'success': result.status.value == 'completed',
                'message': result.message,
                'data': result.data if hasattr(result, 'data') else {},
                'execution_time': result.execution_time if hasattr(result, 'execution_time') else 0
            }
        except Exception as e:
            self.logger.error(f"❌ Ошибка добавления группы: {e}")
            return {'success': False, 'message': f'Ошибка добавления группы: {str(e)}'}
    
    def get_learning_analytics(self) -> Dict[str, Any]:
        """Получение аналитики обучения"""
        if not self.is_initialized or not self.orchestrator:
            return {'success': False, 'message': 'Система не инициализирована'}
        
        try:
            analytics = self.orchestrator.get_learning_analytics()
            
            if analytics:
                return {
                    'success': True,
                    'data': analytics.model_dump() if hasattr(analytics, 'model_dump') else {},
                    'message': 'Аналитика обучения получена'
                }
            else:
                return {'success': False, 'message': 'Аналитика обучения недоступна'}
        except Exception as e:
            self.logger.error(f"❌ Ошибка получения аналитики обучения: {e}")
            return {'success': False, 'message': f'Ошибка получения аналитики: {str(e)}'}
    
    def run_full_training(self) -> Dict[str, Any]:
        """Запуск полного обучения через WorkflowManager"""
        if not self.is_initialized or not self.orchestrator:
            return {'success': False, 'message': 'Система не инициализирована'}
        
        try:
            self.logger.info("🎯 Запуск полного обучения через Telegram бота")
            result = self.orchestrator.workflow_full_training_cycle()
            
            return {
                'success': result.status.value == 'completed',
                'message': result.message,
                'data': result.data if hasattr(result, 'data') else {},
                'execution_time': result.execution_time if hasattr(result, 'execution_time') else 0
            }
        except Exception as e:
            self.logger.error(f"❌ Ошибка полного обучения: {e}")
            return {'success': False, 'message': f'Ошибка обучения: {str(e)}'}
    
    def generate_predictions(self) -> Dict[str, Any]:
        """Генерация новых прогнозов через WorkflowManager"""
        if not self.is_initialized or not self.orchestrator:
            return {'success': False, 'message': 'Система не инициализирована'}
        
        try:
            self.logger.info("🎯 Генерация прогнозов через Telegram бота")
            result = self.orchestrator.workflow_generate_predictions()
            
            return {
                'success': result.status.value == 'completed',
                'message': result.message,
                'data': result.data if hasattr(result, 'data') else {},
                'execution_time': result.execution_time if hasattr(result, 'execution_time') else 0
            }
        except Exception as e:
            self.logger.error(f"❌ Ошибка генерации прогнозов: {e}")
            return {'success': False, 'message': f'Ошибка генерации прогнозов: {str(e)}'}
