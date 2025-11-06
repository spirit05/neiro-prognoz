# ml/core/system.py
"""
Главный интерфейс УСИЛЕННОЙ нейросети - ОПТИМИЗИРОВАННЫЙ
"""

import os
import sys
from typing import List, Tuple

# Добавляем пути для импорта
PROJECT_ROOT = '/home/spirit/Desktop/project'
sys.path.insert(0, PROJECT_ROOT)
sys.path.insert(0, os.path.join(PROJECT_ROOT, 'ml'))

from config.paths import MODEL
from config.logging_config import setup_logger  # Теперь этот импорт должен работать

logger = setup_logger('SimpleNeuralSystem')

class SimpleNeuralSystem:
    def __init__(self):
        self.model_path = MODEL
        self.trainer = None
        self.predictor = None
        self.is_trained = False
        self.progress_callback = None
        self.ensemble_enabled = True
        
        # Ленивая загрузка компонентов
        self._trainer = None
        self._predictor = None
        self._ensemble = None
        self._self_learning = None
        
        self._auto_load_model()
    
    def _get_trainer(self):
        """Ленивая загрузка тренера"""
        if self._trainer is None:
            try:
                from ml.core.trainer import EnhancedTrainer
                self._trainer = EnhancedTrainer(self.model_path)
                if self.progress_callback:
                    self._trainer.set_progress_callback(self.progress_callback)
            except ImportError as e:
                logger.error(f"❌ Не удалось загрузить тренер: {e}")
                self._trainer = None
        return self._trainer
    
    def _get_predictor(self):
        """Ленивая загрузка предсказателя"""
        if self._predictor is None:
            try:
                from ml.core.predictor import EnhancedPredictor
                self._predictor = EnhancedPredictor(self.model_path)
            except ImportError as e:
                logger.error(f"❌ Не удалось загрузить предсказатель: {e}")
                self._predictor = None
        return self._predictor
    
    def _get_ensemble(self):
        """Ленивая загрузка ансамбля"""
        if self._ensemble is None:
            try:
                from ml.ensemble.ensemble import EnsemblePredictor
                self._ensemble = EnsemblePredictor()
                predictor = self._get_predictor()
                if predictor and predictor.is_trained:
                    self._ensemble.set_neural_predictor(predictor)
            except ImportError as e:
                logger.error(f"❌ Не удалось загрузить ансамбль: {e}")
                self._ensemble = None
        return self._ensemble
    
    def _get_self_learning(self):
        """Ленивая загрузка самообучения"""
        if self._self_learning is None:
            try:
                from ml.learning.self_learning import SelfLearningSystem
                self._self_learning = SelfLearningSystem()
            except ImportError as e:
                logger.error(f"❌ Не удалось загрузить самообучение: {e}")
                self._self_learning = None
        return self._self_learning
    
    def _auto_load_model(self):
        """Автоматическая загрузка модели"""
        predictor = self._get_predictor()
        if predictor and predictor.load_model():
            self.is_trained = True
            logger.info("✅ УСИЛЕННАЯ модель автоматически загружена")
        else:
            logger.info("📝 Модель еще не обучена")
    
    def set_progress_callback(self, callback):
        """Установка callback для прогресса"""
        self.progress_callback = callback
        trainer = self._get_trainer()
        if trainer and hasattr(trainer, 'set_progress_callback'):
            trainer.set_progress_callback(callback)
    
    def _report_progress(self, message):
        """Отправка сообщения о прогрессе"""
        if self.progress_callback:
            self.progress_callback(message)
        logger.info(message)
    
    def train(self, epochs: int = 20) -> List[Tuple[Tuple[int, int, int, int], float]]:
        """Обучение УСИЛЕННОЙ системы"""
        try:
            from ml.data.data_loader import load_dataset
            groups = load_dataset()
            
            if not groups or len(groups) < 50:
                self._report_progress(f"❌ Недостаточно данных для обучения: {len(groups)} групп")
                return []
            
            self._report_progress(f"🧠 Обучение УСИЛЕННОЙ нейросети на {len(groups)} группах...")
            
            trainer = self._get_trainer()
            if not trainer:
                self._report_progress("❌ Тренер не доступен")
                return []
            
            result = trainer.train(groups, epochs=epochs)
            self.is_trained = True
            
            # Перезагружаем модель после обучения
            predictor = self._get_predictor()
            if predictor:
                predictor.load_model()
            
            self._report_progress("✅ Обучение завершено и модель загружена!")
            return result
            
        except Exception as e:
            self._report_progress(f"❌ Ошибка обучения: {e}")
            return []
    
    def predict(self, top_k: int = 10) -> List[Tuple[Tuple[int, int, int, int], float]]:
        """Предсказание групп УСИЛЕННОЙ моделью"""
        if not self.is_trained:
            if not self.load():
                self._report_progress("❌ Модель не обучена и не может быть загружена")
                return []
        
        try:
            from ml.data.data_loader import load_dataset
            groups = load_dataset()
            
            if not groups:
                return []
            
            # Используем ансамбль если включен
            if self.ensemble_enabled:
                ensemble = self._get_ensemble()
                if ensemble:
                    try:
                        # Подготавливаем историю для ансамбля
                        recent_numbers = []
                        for group_str in groups[-30:]:
                            try:
                                numbers = [int(x) for x in group_str.strip().split()]
                                if len(numbers) == 4:
                                    recent_numbers.extend(numbers)
                            except:
                                continue
                        
                        if len(recent_numbers) >= 40:
                            predictions = ensemble.predict_ensemble(recent_numbers, top_k)
                            if predictions:
                                self._report_progress(f"🎯 Ансамбль сгенерировал {len(predictions)} предсказаний")
                                return predictions[:top_k]
                    except Exception as e:
                        self._report_progress(f"⚠️  Ансамблевое предсказание не удалось: {e}")
            
            # Резервный вариант: оригинальная модель
            predictor = self._get_predictor()
            if predictor:
                recent_numbers = []
                for group_str in groups[-25:]:
                    try:
                        numbers = [int(x) for x in group_str.strip().split()]
                        if len(numbers) == 4:
                            recent_numbers.extend(numbers)
                    except:
                        continue
                
                if len(recent_numbers) >= 50:
                    predictions = predictor.predict_group(recent_numbers, 15)
                    # Фильтруем слишком слабые предсказания
                    filtered = [(group, score) for group, score in predictions if score > 0.0005]
                    return filtered[:top_k] if filtered else predictions[:top_k]
            
            return []
            
        except Exception as e:
            self._report_progress(f"❌ Ошибка предсказания: {e}")
            return []
    
    def add_data_and_retrain(self, new_group: str, retrain_epochs: int = 5):
        """Добавление данных и дообучение"""
        try:
            from ml.data.data_loader import load_dataset, save_dataset, validate_group
            
            if not validate_group(new_group):
                self._report_progress("❌ Неверный формат группы")
                return []
            
            # Загружаем и обновляем данные
            dataset = load_dataset()
            dataset.append(new_group)
            save_dataset(dataset)
            
            self._report_progress(f"✅ Данные сохранены ({len(dataset)} групп)")
            
            # Анализ точности предыдущих предсказаний
            learning_system = self._get_self_learning()
            if learning_system:
                learning_result = learning_system.analyze_prediction_accuracy(new_group)
                if learning_result:
                    accuracy = learning_result['accuracy_score']
                    matches = learning_result['matches_count']
                    self._report_progress(f"📊 Анализ точности: {matches}/4 совпадений (точность: {accuracy:.1%})")
            
            predictions = []
            
            # Дообучаем модель если она уже была обучена
            if self.is_trained and len(dataset) >= 50:
                self._report_progress("🔄 Дообучение УСИЛЕННОЙ модели на новых данных...")
                
                trainer = self._get_trainer()
                if trainer:
                    trainer.train(dataset, epochs=retrain_epochs)
                    
                    # Перезагружаем модель
                    predictor = self._get_predictor()
                    if predictor:
                        predictor.load_model()
                    
                    self._report_progress("✅ Модель дообучена!")
                    
                    # Делаем прогноз после дообучения
                    predictions = self.predict()
            
            return predictions
            
        except Exception as e:
            self._report_progress(f"❌ Ошибка добавления данных: {e}")
            return []
    
    def load(self) -> bool:
        """Загрузка обученной модели"""
        predictor = self._get_predictor()
        if predictor:
            success = predictor.load_model()
            self.is_trained = success
            return success
        return False
    
    def get_status(self) -> dict:
        """Статус системы"""
        try:
            from ml.data.data_loader import load_dataset
            dataset = load_dataset()
            
            ensemble_info = {
                'ensemble_enabled': self.ensemble_enabled,
                'ensemble_available': self._get_ensemble() is not None,
                'dataset_size_for_ensemble': len(dataset) if dataset else 0
            }
            
            learning_stats = {}
            learning_system = self._get_self_learning()
            if learning_system:
                learning_stats = learning_system.get_performance_stats()
            
            return {
                'is_trained': self.is_trained,
                'dataset_size': len(dataset) if dataset else 0,
                'has_sufficient_data': len(dataset) >= 50 if dataset else False,
                'model_type': 'УСИЛЕННАЯ нейросеть с ансамблем и самообучением',
                'ensemble_info': ensemble_info,
                'learning_stats': learning_stats
            }
        except Exception as e:
            logger.error(f"❌ Ошибка получения статуса: {e}")
            return {
                'is_trained': self.is_trained,
                'dataset_size': 0,
                'has_sufficient_data': False,
                'model_type': 'УСИЛЕННАЯ нейросеть',
                'error': str(e)
            }
    
    def get_learning_insights(self) -> dict:
        """Получение аналитики по самообучению"""
        learning_system = self._get_self_learning()
        if learning_system:
            return learning_system.get_performance_stats()
        return {'message': 'Система самообучения не доступна'}