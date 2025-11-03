# [file name]: model/simple_system.py
"""
Главный интерфейс для УСИЛЕННОЙ нейросети - ОПТИМИЗИРОВАН ДЛЯ WEB
"""

import os
import sys
from typing import List, Tuple

# Правильные абсолютные пути для импортов
current_dir = os.path.dirname(os.path.abspath(__file__))
if current_dir not in sys.path:
    sys.path.insert(0, current_dir)

# Импорты из той же директории model
try:
    from .simple_nn.trainer import EnhancedTrainer
    from .simple_nn.predictor import EnhancedPredictor
    from .data_loader import load_dataset
except ImportError:
    # Альтернативный вариант импорта
    from simple_nn.trainer import EnhancedTrainer
    from simple_nn.predictor import EnhancedPredictor
    from data_loader import load_dataset

class SimpleNeuralSystem:
    def __init__(self):
        self.model_path = "data/simple_model.pth"
        self.trainer = EnhancedTrainer(self.model_path)
        self.predictor = EnhancedPredictor(self.model_path)
        self.is_trained = False
        self.progress_callback = None
        self.ensemble_enabled = True
        
        # Ленивая загрузка ансамблевой системы и самообучения
        self._full_ensemble = None
        self._self_learning = None
        
        self._auto_load_model()
    
    def _get_full_ensemble(self):
        """Ленивая загрузка ансамблевой системы"""
        if self._full_ensemble is None:
            try:
                from .ensemble_predictor import EnsemblePredictor
                self._full_ensemble = EnsemblePredictor()
                print(f"🔍 DEBUG: m/ss загруузка анс системы")
                if self.predictor.is_trained:
                    self._full_ensemble.set_neural_predictor(self.predictor)
                    self._update_full_ensemble()
            except ImportError as e:
                print(f"⚠️  Не удалось загрузить ансамблевую систему: {e}")
                self._full_ensemble = None
        return self._full_ensemble
    
    def _get_self_learning(self):
        """Ленивая загрузка системы самообучения"""
        if self._self_learning is None:
            try:
                from .self_learning import SelfLearningSystem
                self._self_learning = SelfLearningSystem()
            except ImportError as e:
                print(f"⚠️  Не удалось загрузить систему самообучения: {e}")
                self._self_learning = None
        return self._self_learning
    
    def _auto_load_model(self):
        """Автоматическая загрузка модели при инициализации"""
        if os.path.exists(self.model_path):
            if self.predictor.load_model():
                self.is_trained = True
                print("✅ УСИЛЕННАЯ модель автоматически загружена")
                
                # Инициализируем системы если доступны
                self._get_full_ensemble()
                self._get_self_learning()
            else:
                print("❌ Не удалось загрузить модель")
        else:
            print("📝 Модель еще не обучена")
    
    def _update_full_ensemble(self):
        """Обновление данных для полного ансамбля"""
        try:
            dataset = load_dataset()
            ensemble = self._get_full_ensemble()
            if ensemble:
                ensemble.update_ensemble(dataset)
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
    
    def train(self, epochs: int = 20) -> List[Tuple[Tuple[int, int, int, int], float]]:
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
        
        # Запускаем обучение и получаем прогнозы
        result = self.trainer.train(groups, epochs=epochs)
        self.is_trained = True
        
        # Перезагружаем модель после обучения
        self.predictor.load_model()
        
        # Обновляем ансамбль
        self._update_full_ensemble()
        
        self._report_progress("✅ Обучение завершено и модель загружена!")
        return result
    
    def add_data_and_retrain(self, new_group: str, retrain_epochs: int = 5) -> List[Tuple[Tuple[int, int, int, int], float]]:
        """Добавление данных и дообучение УСИЛЕННОЙ модели с возвратом прогнозов"""
        from data_loader import load_dataset, save_dataset, validate_group
        
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
        
        predictions = []
        
        # Всегда обновляем ансамбль
        self._update_full_ensemble()
        
        # Анализ точности предыдущих предсказаний
        learning_system = self._get_self_learning()
        if learning_system:
            learning_result = learning_system.analyze_prediction_accuracy(new_group)
            if learning_result:
                accuracy = learning_result['accuracy_score']
                matches = learning_result['matches_count']
                self._report_progress(f"📊 Анализ точности: {matches}/4 совпадений (точность: {accuracy:.1%})")
        
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
            # Даже если не переобучаем, делаем прогноз на основе ансамбля
            self._report_progress("🔮 Делаем прогноз на основе обновленного ансамбля...")
            predictions = self._make_ensemble_prediction()
        
        return predictions
    
    def _make_prediction(self) -> List[Tuple[Tuple[int, int, int, int], float]]:
        """Внутренний метод для создания прогноза УСИЛЕННОЙ моделью"""
        groups = load_dataset()
        if not groups:
            return []
        
        # Пробуем полный ансамбль сначала
        if self.ensemble_enabled:
            try:
                print("🔍 DEBUG: m/ss  Полный ансамбль начало")
                ensemble_predictions = self._make_ensemble_prediction()
                print(f"🔍 DEBUG: m/ss  Полный ансамбль закончен идем дальше")
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
        for group_str in groups[-30:]:
            try:
                numbers = [int(x) for x in group_str.strip().split()]
                if len(numbers) == 4:
                    recent_numbers.extend(numbers)
            except:
                continue

        print(f"🔍 DEBUG: m/ss история ансамбля {len(recent_numbers)}")
        
        if len(recent_numbers) < 40:
            self._report_progress("❌ Недостаточно данных для ансамблевого предсказания")
            return []
        
        try:
            ensemble = self._get_full_ensemble()
            if ensemble:
                print(f"🔍 DEBUG:m/ss  генерация предсказаний начало")
                predictions = ensemble.predict_ensemble(recent_numbers, 10)
                print(f"🔍 DEBUG: m/ss генерация предсказаний конец - кол-во {len(predictions)}")
                if predictions:
                    self._report_progress(f"🎯 Полный ансамбль сгенерировал {len(predictions)} предсказаний")
                    return predictions[:4]
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
        
        # Информация об ансамбле и самообучении
        ensemble_info = {
            'ensemble_enabled': self.ensemble_enabled,
            'ensemble_available': self._get_full_ensemble() is not None,
            'dataset_size_for_ensemble': len(dataset)
        }
        
        # Статистика самообучения
        learning_stats = {}
        learning_system = self._get_self_learning()
        if learning_system:
            learning_stats = learning_system.get_performance_stats()
        
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
    
    def get_learning_insights(self) -> dict:
        """Получение аналитики по самообучению"""
        learning_system = self._get_self_learning()
        if learning_system:
            return learning_system.get_performance_stats()
        return {'message': 'Система самообучения не доступна'}
    
    def reset_learning_data(self):
        """Сброс данных самообучения"""
        learning_system = self._get_self_learning()
        if learning_system:
            learning_system.reset_learning_data()
            self._report_progress("✅ Данные самообучения сброшены")
        else:
            self._report_progress("❌ Система самообучения не доступна")
