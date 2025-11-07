# [file name]: web/components/ml_adapter.py
"""
Адаптер для интеграции веб-сервиса с новой модульной ML архитектурой
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
    """Главный адаптер для интеграции с новой модульной ML системой"""
    
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
        """Инициализация компонентов новой модульной архитектуры"""
        try:
            # Инициализация тренера
            from ml.core.trainer import EnhancedTrainer
            self.trainer = EnhancedTrainer()
            
            # Инициализация предсказателя
            from ml.core.predictor import EnhancedPredictor
            self.predictor = EnhancedPredictor()
            
            # Инициализация системы самообучения
            from ml.learning.self_learning import SelfLearningSystem
            self.self_learning = SelfLearningSystem()
            
            # Инициализация процессора данных
            from ml.core.data_processor import DataProcessor
            self.data_processor = DataProcessor()
            
            # Попытка загрузить существующую модель
            self._auto_load_model()
            
            logger.info("✅ MLSystemAdapter успешно инициализирован с новой архитектурой")
            
        except ImportError as e:
            logger.error(f"❌ Ошибка инициализации новой архитектуры: {e}")
            raise
    
    def _auto_load_model(self):
        """Автоматическая загрузка обученной модели"""
        if self.predictor.load_model():
            self.is_trained = True
            logger.info("✅ Модель автоматически загружена из новой архитектуры")
        else:
            logger.info("📝 Модель еще не обучена в новой архитектуре")
    
    def set_progress_callback(self, callback):
        """Установка callback для прогресса"""
        self.progress_callback = callback
        if self.trainer:
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
        predictions = self.trainer.train(groups, epochs=epochs)
        
        if predictions:
            self.is_trained = True
            # Перезагружаем модель после обучения
            self.predictor.load_model()
            self._report_progress(f"✅ Обучение завершено! Сгенерировано {len(predictions)} прогнозов")
        else:
            self._report_progress("⚠️ Обучение завершено, но прогнозы не сгенерированы")
        
        return predictions
    
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
        predictions = self.predictor.predict_group(recent_numbers, top_k)
        
        if predictions:
            self._report_progress(f"✅ Сгенерировано {len(predictions)} прогнозов")
        else:
            self._report_progress("⚠️ Прогнозы не сгенерированы")
        
        return predictions
    
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
        if self.self_learning:
            analysis_result = self.self_learning.analyze_prediction_accuracy(sequence_input)
            if analysis_result:
                accuracy = analysis_result['accuracy_score']
                matches = analysis_result['matches_count']
                self._report_progress(f"📊 Анализ точности: {matches}/4 совпадений (точность: {accuracy:.1%})")
        
        predictions = []
        
        # Дообучение если модель уже обучена и есть достаточно данных
        if self.is_trained and len(dataset) >= constants.MIN_DATASET_SIZE:
            self._report_progress("🔄 Дообучение модели на новых данных...")
            predictions = self.trainer.train(dataset, epochs=retrain_epochs)
            
            if predictions:
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
        if self.self_learning:
            learning_stats = self.self_learning.get_performance_stats()
        
        return {
            'is_trained': self.is_trained,
            'model_loaded': self.predictor.is_trained if self.predictor else False,
            'dataset_size': len(dataset),
            'has_sufficient_data': len(dataset) >= constants.MIN_DATASET_SIZE,
            'model_type': 'МОДУЛЬНАЯ УСИЛЕННАЯ НЕЙРОСЕТЬ',
            'learning_stats': learning_stats,
            'architecture': 'НОВАЯ МОДУЛЬНАЯ (ml/)'
        }
    
    def get_learning_insights(self) -> dict:
        """Получение аналитики самообучения"""
        if self.self_learning:
            return self.self_learning.get_performance_stats()
        return {'message': 'Система самообучения не доступна'}
    
    def load(self) -> bool:
        """Загрузка модели"""
        if self.predictor:
            success = self.predictor.load_model()
            self.is_trained = success
            return success
        return False

# Функция для обратной совместимости
def create_ml_system():
    """Создание ML системы (замена SimpleNeuralSystem)"""
    return MLSystemAdapter()