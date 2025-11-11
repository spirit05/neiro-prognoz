# [file name]: ml/core/system_adapter.py
"""
Адаптер для совместимости новой ML системы со старой SimpleNeuralSystem
ИСПРАВЛЕННАЯ ВЕРСИЯ: правильная интеграция дообучения
"""

import os
import sys
from typing import List, Tuple, Dict, Any

# Добавляем пути для импорта
sys.path.insert(0, '/opt/dev')

from ml.learning.self_learning import SelfLearningSystem
from ml.core.data_processor import DataProcessor
from ml.core.predictor import EnhancedPredictor
from ml.core.trainer import EnhancedTrainer
from ml.ensemble.ensemble import EnsemblePredictor
from config.paths import DATA_DIR, MODELS_DIR

# 🔧 ИСПРАВЛЕНИЕ: Добавляем импорт save_predictions
from ml.utils.data_utils import save_predictions

class MLSystemAdapter:
    """Адаптер для совместимости со старой SimpleNeuralSystem - ИСПРАВЛЕННАЯ ВЕРСИЯ"""
    
    def __init__(self):
        self.model_path = os.path.join(MODELS_DIR, "simple_model.pth")
        self.predictor = EnhancedPredictor(self.model_path)
        self.trainer = EnhancedTrainer(self.model_path)
        self.self_learning = SelfLearningSystem()
        self.ensemble_predictor = None
        self.is_trained = False
        self.progress_callback = None
        self.ensemble_enabled = True
        
        self._auto_load_model()
        self._initialize_ensemble()
    
    def _auto_load_model(self):
        """Автоматическая загрузка модели при инициализации"""
        if os.path.exists(self.model_path):
            if self.predictor.load_model():
                self.is_trained = True
                print("✅ УСИЛЕННАЯ модель автоматически загружена")
            else:
                print("❌ Не удалось загрузить модель")
        else:
            print("📝 Модель еще не обучена")
    
    def _initialize_ensemble(self):
        """Инициализация ансамблевой системы"""
        try:
            self.ensemble_predictor = EnsemblePredictor()
            if self.is_trained:
                self.ensemble_predictor.set_neural_predictor(self.predictor)
                self._update_ensemble()
        except Exception as e:
            print(f"⚠️ Не удалось инициализировать ансамбль: {e}")
            self.ensemble_predictor = None
    
    def _update_ensemble(self):
        """Обновление данных для ансамбля"""
        try:
            from ml.utils.data_utils import load_dataset
            dataset = load_dataset()
            if self.ensemble_predictor and dataset:
                self.ensemble_predictor.update_ensemble(dataset)
                print("✅ Ансамбль обновлен с новыми данными")
        except Exception as e:
            print(f"⚠️ Ошибка обновления ансамбля: {e}")
    
    def set_progress_callback(self, callback):
        """Установка callback для прогресса"""
        self.progress_callback = callback
        if self.trainer:
            self.trainer.set_progress_callback(callback)
    
    def _report_progress(self, message):
        """Отправка сообщения о прогрессе"""
        if self.progress_callback:
            self.progress_callback(message)
        else:
            print(f"📢 {message}")
    
    def add_data_and_retrain(self, new_group: str, retrain_epochs: int = 5) -> List[Tuple[Tuple[int, int, int, int], float]]:
        """Добавление данных и дообучение - КЛЮЧЕВОЙ МЕТОД ДЛЯ АВТОСЕРВИСА"""
        try:
            from ml.utils.data_utils import load_dataset, save_dataset, validate_group
            
            if not validate_group(new_group):
                self._report_progress("❌ Неверный формат группы")
                return []
            
            # Загружаем текущие данные
            dataset = load_dataset()
            old_count = len(dataset)
            
            self._report_progress(f"✅ Загружено {old_count} групп из dataset.json")
            
            # Добавляем новую группу
            dataset.append(new_group)
            save_dataset(dataset)
            
            new_count = len(dataset)
            self._report_progress(f"✅ Данные сохранены в dataset.json ({new_count} групп)")
            
            # 🔧 ИСПРАВЛЕНИЕ: Сначала обновляем ансамбль
            self._update_ensemble()
            
            # Анализ точности предыдущих предсказаний
            learning_result = self.self_learning.analyze_prediction_accuracy(new_group)
            if learning_result:
                accuracy = learning_result['accuracy_score']
                matches = learning_result['matches_count']
                self._report_progress(f"📊 Анализ точности: {matches}/4 совпадений (точность: {accuracy:.1%})")
            
            predictions = []
            
            # 🔧 ИСПРАВЛЕНИЕ: Улучшенная логика дообучения
            if self.is_trained and len(dataset) >= 30:  # Уменьшил порог для дообучения
                self._report_progress("🔄 Дообучение УСИЛЕННОЙ модели на новых данных...")
                
                # 🔧 КРИТИЧЕСКОЕ ИСПРАВЛЕНИЕ: Используем флаг is_finetune=True
                predictions = self.trainer.train(dataset, epochs=retrain_epochs, is_finetune=True)
                
                # Перезагружаем модель после дообучения
                self.predictor.load_model()
                
                # 🔧 ИСПРАВЛЕНИЕ: Обновляем ансамбль после дообучения
                self._update_ensemble()
                
                self._report_progress("✅ Модель дообучена и ансамбль обновлен!")
                
            elif not self.is_trained and len(dataset) >= 50:
                self._report_progress("🎯 Достаточно данных для первого обучения УСИЛЕННОЙ модели!")
                predictions = self.train(epochs=20)
            else:
                # Даже если не переобучаем, делаем прогноз на основе обновленного ансамбля
                self._report_progress("🔮 Делаем прогноз на основе обновленного ансамбля...")
                predictions = self._make_ensemble_prediction()
            
            return predictions
            
        except Exception as e:
            self._report_progress(f"❌ Ошибка в add_data_and_retrain: {e}")
            return []
    
    def train(self, epochs: int = 20) -> List[Tuple[Tuple[int, int, int, int], float]]:
        """Обучение системы с возвратом прогнозов"""
        from ml.utils.data_utils import load_dataset
        
        groups = load_dataset()
        if not groups:
            self._report_progress("❌ Нет данных для обучения")
            return []
        
        if len(groups) < 50:
            self._report_progress(f"❌ Недостаточно данных для обучения: {len(groups)} групп (нужно минимум 50)")
            return []
        
        self._report_progress(f"🧠 Обучение УСИЛЕННОЙ нейросети на {len(groups)} группах...")
        
        # Запускаем обучение
        result = self.trainer.train(groups, epochs=epochs, is_finetune=False)
        self.is_trained = True
        
        # Перезагружаем модель после обучения
        self.predictor.load_model()
        
        # Обновляем ансамбль
        self._update_ensemble()
        
        self._report_progress("✅ Обучение завершено и модель загружена!")
        return result
    
    def _make_prediction(self) -> List[Tuple[Tuple[int, int, int, int], float]]:
        """Создание прогноза"""
        from ml.utils.data_utils import load_dataset
        
        groups = load_dataset()
        if not groups:
            return []
        
        # Пробуем ансамбль сначала
        if self.ensemble_enabled and self.ensemble_predictor:
            try:
                ensemble_predictions = self._make_ensemble_prediction()
                if ensemble_predictions:
                    return ensemble_predictions
            except Exception as e:
                self._report_progress(f"⚠️ Ансамблевое предсказание не удалось: {e}")
        
        # Резервный вариант: оригинальная логика
        recent_numbers = []
        for group_str in groups[-25:]:
            try:
                numbers = [int(x) for x in group_str.strip().split()]
                if len(numbers) == 4:
                    recent_numbers.extend(numbers)
            except:
                continue
        
        if len(recent_numbers) < 50:
            self._report_progress("❌ Недостаточно данных для предсказания")
            return []
        
        predictions = self.predictor.predict_group(recent_numbers, 15)
        
        # Фильтруем слишком слабые предсказания
        filtered_predictions = [(group, score) for group, score in predictions if score > 0.0005]
        if not filtered_predictions:
            self._report_progress("⚠️ Все предсказания имеют низкую уверенность")
            best_predictions = sorted(predictions, key=lambda x: x[1], reverse=True)[:4]
            return best_predictions
        
        return filtered_predictions[:4]
    
    def _make_ensemble_prediction(self) -> List[Tuple[Tuple[int, int, int, int], float]]:
        """Прогноз с использованием ансамбля"""
        from ml.utils.data_utils import load_dataset
        
        groups = load_dataset()
        if not groups or not self.ensemble_predictor:
            return []
        
        # Подготавливаем историю для ансамбля
        recent_numbers = []
        for group_str in groups[-30:]:
            try:
                numbers = [int(x) for x in group_str.strip().split()]
                if len(numbers) == 4:
                    recent_numbers.extend(numbers)
            except:
                continue
        
        if len(recent_numbers) < 40:
            self._report_progress("❌ Недостаточно данных для ансамблевого предсказания")
            return []
        
        try:
            predictions = self.ensemble_predictor.predict_ensemble(recent_numbers, 10)
            if predictions:
                self._report_progress(f"🎯 Ансамбль сгенерировал {len(predictions)} предсказаний")
                return predictions[:4]
        except Exception as e:
            self._report_progress(f"❌ Ошибка ансамбля: {e}")
        
        return []
    
    def get_status(self) -> dict:
        """Статус системы"""
        from ml.utils.data_utils import load_dataset
        
        dataset = load_dataset()
        
        return {
            'is_trained': self.is_trained,
            'model_loaded': self.predictor.is_trained,
            'dataset_size': len(dataset),
            'has_sufficient_data': len(dataset) >= 50,
            'model_type': 'УСИЛЕННАЯ нейросеть с ансамблем и самообучением',
            'ensemble_available': self.ensemble_predictor is not None,
            'self_learning_available': True
        }
    
    def get_learning_insights(self) -> dict:
        """Получение аналитики по самообучению"""
        return self.self_learning.get_performance_stats()
    
    def predict(self, top_k: int = 10) -> List[Tuple[Tuple[int, int, int, int], float]]:
        """Предсказание групп"""
        if not self.is_trained:
            if not self.load():
                self._report_progress("❌ Модель не обучена и не может быть загружена")
                return []
        
        return self._make_prediction()
    
    def load(self) -> bool:
        """Загрузка обученной модели"""
        success = self.predictor.load_model()
        self.is_trained = success
        
        if success:
            self._update_ensemble()
        
        return success
