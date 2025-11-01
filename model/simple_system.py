# [file name]: model/simple_system.py (ПОЛНОСТЬЮ ОБНОВЛЕННЫЙ)
"""
Главный интерфейс для УСИЛЕННОЙ нейросети с ансамблевыми методами и самообучением
"""

import os
import sys
from typing import List, Tuple

# Добавляем родительскую директорию в путь для импортов
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

# Правильные импорты
from model.simple_nn.trainer import EnhancedTrainer
from model.simple_nn.predictor import EnhancedPredictor
from model.data_loader import load_dataset
from model.ensemble_predictor import EnsemblePredictor
from model.self_learning import SelfLearningSystem

class SimpleNeuralSystem:
    def __init__(self):
        self.model_path = "data/simple_model.pth"
        self.trainer = EnhancedTrainer(self.model_path)
        self.predictor = EnhancedPredictor(self.model_path)
        self.is_trained = False
        self.progress_callback = None
        self.ensemble_enabled = True
        
        # НОВОЕ: Полная ансамблевая система
        self.full_ensemble = EnsemblePredictor()
        
        # НОВОЕ: Система самообучения
        self.self_learning = SelfLearningSystem()
        
        self._auto_load_model()
    
    def _auto_load_model(self):
        """Автоматическая загрузка модели при инициализации"""
        if os.path.exists(self.model_path):
            if self.predictor.load_model():
                self.is_trained = True
                
                # НОВОЕ: Инициализируем полный ансамбль
                self.full_ensemble.set_neural_predictor(self.predictor)
                self._update_full_ensemble()
                
                print("✅ УСИЛЕННАЯ модель автоматически загружена")
                print("✅ Ансамблевая система инициализирована")
                print("✅ Система самообучения активирована")
            else:
                print("❌ Не удалось загрузить модель")
        else:
            print("📝 Модель еще не обучена")
    
    def _update_full_ensemble(self):
        """Обновление данных для полного ансамбля"""
        try:
            dataset = load_dataset()
            self.full_ensemble.update_ensemble(dataset)
        except Exception as e:
            print(f"⚠️  Ошибка обновления полного ансамбля: {e}")
    
    def set_progress_callback(self, callback):
        """Установка callback для прогресса"""
        self.progress_callback = callback
        if hasattr(self.trainer, 'set_progress_callback'):
            self.trainer.set_progress_callback(callback)
    
    def _report_progress(self, message):
        """Отправка сообщения о прогрессе"""
        if self.progress_callback:
            self.progress_callback(message)
        else:
            print(f"📢 {message}")
    
    def train(self, epochs: int = 25) -> List[Tuple[Tuple[int, int, int, int], float]]:
        """Обучение УСИЛЕННОЙ системы с возвратом прогнозов"""
        groups = load_dataset()
        if not groups:
            self._report_progress("❌ Нет данных для обучения")
            return []
        
        if len(groups) < 50:
            self._report_progress(f"❌ Недостаточно данных для обучения: {len(groups)} групп (нужно минимум 50)")
            return []
        
        self._report_progress(f"🧠 Обучение УСИЛЕННОЙ нейросети на {len(groups)} группах...")
        
        # Устанавливаем callback в trainer
        if hasattr(self.trainer, 'set_progress_callback'):
            self.trainer.set_progress_callback(self.progress_callback)
        
        self.trainer.train(groups, epochs=epochs)
        self.is_trained = True
        
        # Перезагружаем модель после обучения
        self.predictor.load_model()
        
        # НОВОЕ: Обновляем ансамбль
        self._update_full_ensemble()
        
        self._report_progress("✅ Обучение завершено и модель загружена!")
        self._report_progress("✅ Ансамблевая система обновлена!")
        
        # Делаем прогноз после обучения
        self._report_progress("🔮 Делаем прогноз после обучения...")
        predictions = self._make_prediction()
        return predictions
    
    def add_data_and_retrain(self, new_group: str, retrain_epochs: int = 5) -> List[Tuple[Tuple[int, int, int, int], float]]:
        """Добавление данных и дообучение УСИЛЕННОЙ модели с возвратом прогнозов"""
        from model.data_loader import load_dataset, save_dataset, validate_group
        
        if not validate_group(new_group):
            self._report_progress("❌ Неверный формат группы")
            return []
        
        # Загружаем текущие данные
        dataset = load_dataset()
        old_count = len(dataset)
        
        self._report_progress(f"✅ Загружено {old_count} групп из dataset.json")
        
        dataset.append(new_group)
        save_dataset(dataset)
        
        new_count = len(dataset)
        self._report_progress(f"✅ Данные сохранены в dataset.json ({new_count} групп)")
        self._report_progress(f"✅ Группа добавлена. Всего групп: {new_count}")
        
        predictions = []
        
        # НОВОЕ: Всегда обновляем ансамбль
        self._update_full_ensemble()
        
        # НОВОЕ: Анализ точности предыдущих предсказаний
        learning_result = self.self_learning.analyze_prediction_accuracy(new_group)
        if learning_result:
            accuracy = learning_result['accuracy_score']
            matches = learning_result['matches_count']
            self._report_progress(f"📊 Анализ точности: {matches}/4 совпадений (точность: {accuracy:.1%})")
            
            # Автоматическая корректировка весов ансамбля
            if self.self_learning.adjust_ensemble_weights(self.full_ensemble):
                self._report_progress("🔧 Веса ансамбля скорректированы на основе точности")
            
            # Показ рекомендаций
            recommendations = self.self_learning.get_learning_recommendations()
            for rec in recommendations:
                self._report_progress(f"💡 {rec}")
        
        # Дообучаем модель если она уже была обучена и есть достаточно данных
        if self.is_trained and len(dataset) >= 50:
            self._report_progress("🔄 Дообучение УСИЛЕННОЙ модели на новых данных...")
            
            # Устанавливаем callback в trainer
            if hasattr(self.trainer, 'set_progress_callback'):
                self.trainer.set_progress_callback(self.progress_callback)
            
            self.trainer.train(dataset, epochs=retrain_epochs)
            self.predictor.load_model()
            self._report_progress("✅ Модель дообучена!")
            
            # Делаем прогноз после дообучения
            self._report_progress("🔮 Делаем прогноз после дообучения...")
            predictions = self._make_prediction()
            
        elif not self.is_trained and len(dataset) >= 50:
            self._report_progress("🎯 Достаточно данных для первого обучения УСИЛЕННОЙ модели!")
            predictions = self.train(epochs=20)
        else:
            # НОВОЕ: Даже если не переобучаем, делаем прогноз на основе ансамбля
            self._report_progress("🔮 Делаем прогноз на основе обновленного ансамбля...")
            predictions = self._make_ensemble_prediction()
        
        return predictions
    
    def _make_prediction(self) -> List[Tuple[Tuple[int, int, int, int], float]]:
        """Внутренний метод для создания прогноза УСИЛЕННОЙ моделью"""
        groups = load_dataset()
        if not groups:
            return []
        
        # НОВОЕ: Пробуем полный ансамбль сначала
        if self.ensemble_enabled:
            try:
                ensemble_predictions = self._make_ensemble_prediction()
                if ensemble_predictions:
                    return ensemble_predictions
            except Exception as e:
                self._report_progress(f"⚠️  Ансамблевое предсказание не удалось: {e}")
        
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
            self._report_progress("⚠️  Все предсказания имеют низкую уверенность")
            # Возвращаем топ-4 даже если слабые, но с лучшими score
            best_predictions = sorted(predictions, key=lambda x: x[1], reverse=True)[:4]
            return best_predictions
        
        return filtered_predictions[:4]
    
    def _make_ensemble_prediction(self) -> List[Tuple[Tuple[int, int, int, int], float]]:
        """Прогноз с использованием полного ансамбля"""
        groups = load_dataset()
        if not groups:
            return []
        
        # Подготавливаем историю для ансамбля
        recent_numbers = []
        for group_str in groups[-30:]:  # Берем больше истории для ансамбля
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
            predictions = self.full_ensemble.predict_ensemble(recent_numbers, 10)
            if predictions:
                self._report_progress(f"🎯 Полный ансамбль сгенерировал {len(predictions)} предсказаний")
                return predictions[:8]  # Возвращаем топ-8
        except Exception as e:
            self._report_progress(f"❌ Ошибка полного ансамбля: {e}")
        
        return []
    
    def load(self) -> bool:
        """Загрузка обученной модели"""
        success = self.predictor.load_model()
        self.is_trained = success
        
        if success:
            self._update_full_ensemble()
        
        return success
    
    def predict(self, top_k: int = 10) -> List[Tuple[Tuple[int, int, int, int], float]]:
        """Предсказание групп УСИЛЕННОЙ моделью"""
        if not self.is_trained:
            if not self.load():
                self._report_progress("❌ Модель не обучена и не может быть загружена")
                return []
        
        return self._make_prediction()
    
    def get_status(self) -> dict:
        """Статус системы"""
        dataset = load_dataset()
        
        # НОВОЕ: Информация об ансамбле и самообучении
        ensemble_info = {
            'ensemble_enabled': self.ensemble_enabled,
            'ensemble_components': len([p for p in self.full_ensemble.predictors.values() if p is not None]),
            'dataset_size_for_ensemble': len(dataset)
        }
        
        # НОВОЕ: Статистика самообучения
        learning_stats = self.self_learning.get_performance_stats()
        
        return {
            'is_trained': self.is_trained,
            'model_loaded': self.predictor.is_trained,
            'model_path': self.predictor.model_path,
            'dataset_size': len(dataset),
            'has_sufficient_data': len(dataset) >= 50,
            'model_type': 'УСИЛЕННАЯ нейросеть с ансамблем и самообучением',
            'ensemble_info': ensemble_info,
            'learning_stats': learning_stats
        }
    
    def toggle_ensemble(self, enable: bool = None):
        """Включение/выключение ансамблевого режима"""
        if enable is None:
            enable = not self.ensemble_enabled
        
        self.ensemble_enabled = enable
        self.predictor.enable_ensemble(enable)
        
        status = "включен" if enable else "выключен"
        self._report_progress(f"🔧 Ансамблевый режим {status}")
        
        return enable
    
    # НОВЫЕ МЕТОДЫ ДЛЯ САМООБУЧЕНИЯ
    
    def get_learning_insights(self) -> Dict:
        """Получение аналитики по самообучению"""
        return self.self_learning.get_performance_stats()
    
    def reset_learning_data(self):
        """Сброс данных самообучения"""
        self.self_learning.reset_learning_data()
        self._report_progress("✅ Данные самообучения сброшены")
    
    def analyze_accuracy(self, actual_group: str) -> Dict:
        """Ручной анализ точности для конкретной группы"""
        return self.self_learning.analyze_prediction_accuracy(actual_group)