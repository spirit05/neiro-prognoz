# ml/core/system.py - ИСПРАВЛЯЕМ ЛОГГЕР

import os
import sys
from typing import List, Tuple

# Добавляем пути для импорта
PROJECT_ROOT = '/home/spirit/Desktop/project'
sys.path.insert(0, PROJECT_ROOT)
sys.path.insert(0, os.path.join(PROJECT_ROOT, 'ml'))

from config.paths import MODEL
from utils.logging_system import get_ml_system_logger  # ← ИСПРАВЛЕННЫЙ ИМПОРТ

logger = get_ml_system_logger()  # ← ИСПРАВЛЕННЫЙ ЛОГГЕР

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
        
        logger.info("✅ SimpleNeuralSystem инициализирован")  # ← ИСПРАВЛЕННЫЙ ЛОГГЕР
    
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
            logger.info("✅ УСИЛЕННАЯ модель автоматически загружена")  # ← ИСПРАВЛЕННЫЙ ЛОГГЕР
        else:
            logger.info("🔰 Модель еще не обучена")  # ← ИСПРАВЛЕННЫЙ ЛОГГЕР
    
    def _report_progress(self, message):
        """Отправка сообщения о прогрессе"""
        if self.progress_callback:
            self.progress_callback(message)
        logger.info(message)  # ← ИСПРАВЛЕННЫЙ ЛОГГЕР
    
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

            # Перезагружаем модель после обучения
            predictor = self._get_predictor()
            if predictor:
                predictor.load_model()

            self._report_progress("✅ Обучение завершено и модель загружена!")
            return result

        except Exception as e:
            self._report_progress(f"❌ Ошибка обучения: {e}")
            return []