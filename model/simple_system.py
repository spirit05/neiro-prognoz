# model/simple_system.py
"""
Главный интерфейс для УСИЛЕННОЙ нейросети
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

class SimpleNeuralSystem:
    def __init__(self):
        self.model_path = "data/simple_model.pth"
        self.trainer = EnhancedTrainer(self.model_path)
        self.predictor = EnhancedPredictor(self.model_path)
        self.is_trained = False
        self.progress_callback = None  # Добавляем callback
        self._auto_load_model()
    
    def set_progress_callback(self, callback):
        """Установка callback для прогресса"""
        self.progress_callback = callback
        if hasattr(self.trainer, 'set_progress_callback'):
            self.trainer.set_progress_callback(callback)
    
    def _report_progress(self, message):
        """Отправка сообщения о прогрессе"""
        if self.progress_callback:
            self.progress_callback(message)

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
    
    def add_data_and_retrain(self, new_group: str, retrain_epochs: int = 10) -> List[Tuple[Tuple[int, int, int, int], float]]:
        """Добавление данных и дообучение с прогрессом"""
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
            self._report_progress("🎯 Достаточно данных для первого обучения!")
            predictions = self.train(epochs=20)
        
        return predictions
    
    def train(self, epochs: int = 25) -> List[Tuple[Tuple[int, int, int, int], float]]:
        """Обучение системы с прогрессом"""
        groups = load_dataset()
        if not groups:
            self._report_progress("❌ Нет данных для обучения")
            return []
        
        if len(groups) < 50:
            self._report_progress(f"❌ Недостаточно данных для обучения: {len(groups)} групп")
            return []
        
        self._report_progress(f"🧠 Обучение УСИЛЕННОЙ нейросети на {len(groups)} группах...")
        
        # Устанавливаем callback в trainer
        if hasattr(self.trainer, 'set_progress_callback'):
            self.trainer.set_progress_callback(self.progress_callback)
        
        self.trainer.train(groups, epochs=epochs)
        self.is_trained = True
        self.predictor.load_model()
        self._report_progress("✅ Обучение завершено и модель загружена!")
        
        # Делаем прогноз после обучения
        self._report_progress("🔮 Делаем прогноз после обучения...")
        predictions = self._make_prediction()
        return predictions
    
    def _make_prediction(self) -> List[Tuple[Tuple[int, int, int, int], float]]:
        """Внутренний метод для создания прогноза УСИЛЕННОЙ моделью"""
        groups = load_dataset()
        if not groups:
            return []
        
        # Берем больше истории для лучшего предсказания
        recent_numbers = []
        for group_str in groups[-25:]:  # Увеличили историю для усиленной модели
            try:
                numbers = [int(x) for x in group_str.strip().split()]
                if len(numbers) == 4:
                    recent_numbers.extend(numbers)
            except:
                continue
        
        if len(recent_numbers) < 50:  # Увеличили минимальную историю
            print("❌ Недостаточно данных для предсказания")
            return []
        
        predictions = self.predictor.predict_group(recent_numbers, 15)  # Берем больше кандидатов
        
        # Фильтруем слишком слабые предсказания
        filtered_predictions = [(group, score) for group, score in predictions if score > 0.0005]  # Повысили порог
        
        if not filtered_predictions:
            print("⚠️  Все предсказания имеют низкую уверенность")
            # Возвращаем топ-4 даже если слабые, но с лучшими score
            best_predictions = sorted(predictions, key=lambda x: x[1], reverse=True)[:4]
            return best_predictions
        
        return filtered_predictions[:4]
    
    def load(self) -> bool:
        """Загрузка обученной модели"""
        success = self.predictor.load_model()
        self.is_trained = success
        return success
    
    def predict(self, top_k: int = 10) -> List[Tuple[Tuple[int, int, int, int], float]]:
        """Предсказание групп УСИЛЕННОЙ моделью"""
        if not self.is_trained:
            if not self.load():
                print("❌ Модель не обучена и не может быть загружена")
                return []
        
        return self._make_prediction()
    
    def get_status(self) -> dict:
        """Статус системы"""
        dataset = load_dataset()
        return {
            'is_trained': self.is_trained,
            'model_loaded': self.predictor.is_trained,
            'model_path': self.predictor.model_path,
            'dataset_size': len(dataset),
            'has_sufficient_data': len(dataset) >= 50,
            'model_type': 'УСИЛЕННАЯ нейросеть'
        }