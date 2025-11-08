# [file name]: web/components/ml_adapter.py
"""
Адаптер для интеграции веб-сервиса с новой модульной ML архитектурой - ИСПРАВЛЕННАЯ ВЕРСИЯ
"""

import sys
import os
from typing import List, Tuple, Dict
import logging

# Добавляем пути новой архитектуры
sys.path.insert(0, '/opt/dev')

from config import paths, constants, logging_config

logger = logging_config.get_ml_system_logger()

class MLSystemAdapter:
    """Главный адаптер для интеграции с новой модульной ML системой - ИСПРАВЛЕННАЯ ВЕРСИЯ"""
    
    def __init__(self):
        self.is_trained = False
        self.progress_callback = None
        
        # Компоненты новой архитектуры
        self.trainer = None
        self.predictor = None
        self.self_learning = None
        self.ensemble = None
        self.data_processor = None
        
        self._initialize_new_architecture()
    
    def _initialize_new_architecture(self):
        """Инициализация компонентов новой модульной архитектуры - ИСПРАВЛЕННЫЕ ИМПОРТЫ"""
        try:
            # ⚡ ПРАВИЛЬНЫЕ ИМПОРТЫ из новой архитектуры
            from ml.core.trainer import EnhancedTrainer
            from ml.core.predictor import EnhancedPredictor
            from ml.learning.self_learning import SelfLearningSystem
            from ml.core.data_processor import DataProcessor
            
            # Инициализация тренера
            self.trainer = EnhancedTrainer()
            
            # Инициализация предсказателя
            self.predictor = EnhancedPredictor()
            
            # Инициализация системы самообучения
            self.self_learning = SelfLearningSystem()
            
            # Инициализация процессора данных
            self.data_processor = DataProcessor()
            
            # Попытка загрузить существующую модель
            self._auto_load_model()
            
            logger.info("✅ MLSystemAdapter успешно инициализирован с новой архитектурой")
            
        except ImportError as e:
            logger.error(f"❌ Ошибка инициализации новой архитектуры: {e}")
            # Создаем заглушки для тестирования
            self._create_mock_components()
    
    def _create_mock_components(self):
        """Создание mock компонентов для тестирования при ошибках импорта"""
        class MockTrainer:
            def set_progress_callback(self, callback): pass
            def train(self, groups, epochs=None): return []
        
        class MockPredictor:
            def __init__(self): self.is_trained = False
            def load_model(self): return False
            def predict_group(self, history, top_k=None): return []
        
        class MockSelfLearning:
            def analyze_prediction_accuracy(self, actual_group): return None
            def get_performance_stats(self): return {'message': 'Mock system'}
        
        self.trainer = MockTrainer()
        self.predictor = MockPredictor()
        self.self_learning = MockSelfLearning()
        logger.info("⚠️  Созданы mock компоненты для тестирования")
    
    def _auto_load_model(self):
        """Автоматическая загрузка обученной модели"""
        if self.predictor and hasattr(self.predictor, 'load_model'):
            if self.predictor.load_model():
                self.is_trained = True
                logger.info("✅ Модель автоматически загружена из новой архитектуры")
            else:
                logger.info("📝 Модель еще не обучена в новой архитектуре")
    
    def set_progress_callback(self, callback):
        """Установка callback для прогресса"""
        self.progress_callback = callback
        if self.trainer and hasattr(self.trainer, 'set_progress_callback'):
            self.trainer.set_progress_callback(callback)
    
    def _report_progress(self, message):
        """Отправка сообщения о прогрессе"""
        logger.info(message)
        if self.progress_callback:
            self.progress_callback(message)
    
    def train(self, epochs: int = None) -> List[Tuple[Tuple[int, int, int, int], float]]:
        """Обучение модели в новой архитектуре"""
        if epochs is None:
            epochs = constants.MAIN_TRAINING_EPOCHS
            
        from ml.utils.data_utils import load_dataset
        groups = load_dataset()
        
        if not groups:
            self._report_progress("❌ Нет данных для обучения")
            return []
        
        if len(groups) < constants.MIN_DATASET_SIZE:
            self._report_progress(f"❌ Недостаточно данных: {len(groups)} групп (нужно {constants.MIN_DATASET_SIZE})")
            return []
        
        self._report_progress(f"🧠 Обучение модели на {len(groups)} группах...")
        
        # Запускаем обучение через нового тренера
        if self.trainer and hasattr(self.trainer, 'train'):
            predictions = self.trainer.train(groups, epochs=epochs)
            
            if predictions:
                self.is_trained = True
                # Перезагружаем модель после обучения
                if self.predictor and hasattr(self.predictor, 'load_model'):
                    self.predictor.load_model()
                self._report_progress(f"✅ Обучение завершено! Сгенерировано {len(predictions)} прогнозов")
            else:
                self._report_progress("⚠️ Обучение завершено, но прогнозы не сгенерированы")
            
            return predictions
        else:
            self._report_progress("❌ Тренер не доступен")
            return []
    
    def predict(self, top_k: int = None) -> List[Tuple[Tuple[int, int, int, int], float]]:
        """Прогнозирование в новой архитектуре"""
        if top_k is None:
            top_k = constants.PREDICTION_TOP_K
            
        if not self.is_trained:
            self._report_progress("❌ Модель не обучена")
            return []
        
        from ml.utils.data_utils import load_dataset
        groups = load_dataset()
        
        if not groups:
            self._report_progress("❌ Нет данных для прогнозирования")
            return []
        
        # Подготавливаем историю для предсказания
        recent_numbers = []
        for group_str in groups[-25:]:  # Берем последние 25 групп
            try:
                numbers = [int(x) for x in group_str.strip().split()]
                if len(numbers) == 4:
                    recent_numbers.extend(numbers)
            except:
                continue
        
        if len(recent_numbers) < 50:
            self._report_progress("❌ Недостаточно данных для предсказания")
            return []
        
        self._report_progress("🔮 Генерация прогнозов...")
        
        if self.predictor and hasattr(self.predictor, 'predict_group'):
            predictions = self.predictor.predict_group(recent_numbers, top_k)
            
            if predictions:
                self._report_progress(f"✅ Сгенерировано {len(predictions)} прогнозов")
            else:
                self._report_progress("⚠️ Прогнозы не сгенерированы")
            
            return predictions
        else:
            self._report_progress("❌ Предсказатель не доступен")
            return []
    
    def add_data_and_retrain(self, sequence_input: str, retrain_epochs: int = None) -> List[Tuple[Tuple[int, int, int, int], float]]:
        """Добавление данных и дообучение в новой архитектуре"""
        if retrain_epochs is None:
            retrain_epochs = constants.RETRAIN_EPOCHS
            
        from ml.utils.data_utils import load_dataset, save_dataset, validate_group
        
        if not validate_group(sequence_input):
            self._report_progress("❌ Неверный формат группы")
            return []
        
        # Загружаем и обновляем данные
        dataset = load_dataset()
        old_count = len(dataset)
        
        dataset.append(sequence_input)
        save_dataset(dataset)
        
        new_count = len(dataset)
        self._report_progress(f"✅ Данные сохранены: {old_count} → {new_count} групп")
        
        # Анализ точности предыдущих прогнозов
        if self.self_learning and hasattr(self.self_learning, 'analyze_prediction_accuracy'):
            analysis_result = self.self_learning.analyze_prediction_accuracy(sequence_input)
            if analysis_result:
                accuracy = analysis_result['accuracy_score']
                matches = analysis_result['matches_count']
                self._report_progress(f"📊 Анализ точности: {matches}/4 совпадений (точность: {accuracy:.1%})")
        
        predictions = []
        
        # Дообучение если модель уже обучена и есть достаточно данных
        if self.is_trained and len(dataset) >= constants.MIN_DATASET_SIZE:
            self._report_progress("🔄 Дообучение модели на новых данных...")
            
            if self.trainer and hasattr(self.trainer, 'train'):
                predictions = self.trainer.train(dataset, epochs=retrain_epochs)
                
                if predictions:
                    if self.predictor and hasattr(self.predictor, 'load_model'):
                        self.predictor.load_model()
                    self._report_progress("✅ Модель дообучена!")
                else:
                    self._report_progress("⚠️ Дообучение завершено, но прогнозы не сгенерированы")
                    
        elif not self.is_trained and len(dataset) >= constants.MIN_DATASET_SIZE:
            self._report_progress("🎯 Достаточно данных для первого обучения!")
            predictions = self.train(epochs=constants.MAIN_TRAINING_EPOCHS)
        else:
            # Если не переобучаем, делаем обычный прогноз
            self._report_progress("🔮 Делаем прогноз на обновленных данных...")
            predictions = self.predict()
        
        return predictions
    
    def get_status(self) -> dict:
        """Получение статуса системы из новой архитектуры"""
        from ml.utils.data_utils import load_dataset
        dataset = load_dataset()
        
        # Статистика самообучения
        learning_stats = {}
        if self.self_learning and hasattr(self.self_learning, 'get_performance_stats'):
            learning_stats = self.self_learning.get_performance_stats()
        
        return {
            'is_trained': self.is_trained,
            'model_loaded': self.predictor.is_trained if self.predictor and hasattr(self.predictor, 'is_trained') else False,
            'dataset_size': len(dataset),
            'has_sufficient_data': len(dataset) >= constants.MIN_DATASET_SIZE,
            'model_type': 'МОДУЛЬНАЯ УСИЛЕННАЯ НЕЙРОСЕТЬ',
            'learning_stats': learning_stats,
            'architecture': 'НОВАЯ МОДУЛЬНАЯ (ml/)'
        }
    
    def get_learning_insights(self) -> dict:
        """Получение аналитики самообучения"""
        if self.self_learning and hasattr(self.self_learning, 'get_performance_stats'):
            return self.self_learning.get_performance_stats()
        return {'message': 'Система самообучения не доступна'}
    
    def load(self) -> bool:
        """Загрузка модели"""
        if self.predictor and hasattr(self.predictor, 'load_model'):
            success = self.predictor.load_model()
            self.is_trained = success
            return success
        return False

# Функция для обратной совместимости
def create_ml_system():
    """Создание ML системы (замена SimpleNeuralSystem)"""
    return MLSystemAdapter()

