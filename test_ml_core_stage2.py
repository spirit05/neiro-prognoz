#!/usr/bin/env python3
"""
ТЕСТ ЭТАПА 2 - ML СИСТЕМА ЯДРО
Запуск: python3 /opt/dev/test_ml_core_stage2.py
"""

import sys
import os

def test_ml_core_system():
    """Тестирование ML ядра системы ЭТАПА 2"""
    print("🧪 ТЕСТ ML СИСТЕМЫ ЯДРО - ЭТАП 2")
    print("=" * 60)
    
    # Добавляем путь к проекту
    sys.path.insert(0, '/opt/dev')
    
    try:
        # 1. ТЕСТ ИМПОРТОВ ML ЯДРА
        print("1. 🔄 Тест импорта ML модулей...")
        
        try:
            from ml.core.model import EnhancedNumberPredictor
            print("   ✅ ml.core.model - УСПЕХ")
        except ImportError as e:
            print(f"   ❌ ml.core.model: {e}")
            return False
        
        try:
            from ml.core.trainer import EnhancedTrainer
            print("   ✅ ml.core.trainer - УСПЕХ")
        except ImportError as e:
            print(f"   ❌ ml.core.trainer: {e}")
            return False
        
        try:
            from ml.core.predictor import EnhancedPredictor
            print("   ✅ ml.core.predictor - УСПЕХ")
        except ImportError as e:
            print(f"   ❌ ml.core.predictor: {e}")
            return False
        
        try:
            from ml.core.data_processor import DataProcessor
            print("   ✅ ml.core.data_processor - УСПЕХ")
        except ImportError as e:
            print(f"   ❌ ml.core.data_processor: {e}")
            return False
        
        try:
            from ml.features.extractor import FeatureExtractor
            print("   ✅ ml.features.extractor - УСПЕХ")
        except ImportError as e:
            print(f"   ❌ ml.features.extractor: {e}")
            return False
        
        try:
            from ml.utils.data_utils import load_dataset, save_dataset, validate_group
            print("   ✅ ml.utils.data_utils - УСПЕХ")
        except ImportError as e:
            print(f"   ❌ ml.utils.data_utils: {e}")
            return False
        
        # 2. ТЕСТ МОДЕЛИ
        print("\n2. 🔧 Тест создания модели...")
        try:
            model = EnhancedNumberPredictor(input_size=50, hidden_size=256)
            print("   ✅ Модель создана успешно")
            
            # Тест forward pass
            import torch
            test_input = torch.randn(1, 50)
            output = model(test_input)
            print(f"   ✅ Forward pass: вход {test_input.shape} -> выход {output.shape}")
            
        except Exception as e:
            print(f"   ❌ Ошибка модели: {e}")
            return False
        
        # 3. ТЕСТ ИЗВЛЕЧЕНИЯ ПРИЗНАКОВ
        print("\n3. 📊 Тест извлечения признаков...")
        try:
            extractor = FeatureExtractor(history_size=20)
            test_history = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20]
            features = extractor.extract_features(test_history)
            print(f"   ✅ Извлечено признаков: {len(features)}")
            print(f"   📈 Размер признаков: {features.shape}")
            
        except Exception as e:
            print(f"   ❌ Ошибка извлечения признаков: {e}")
            return False
        
        # 4. ТЕСТ ОБРАБОТКИ ДАННЫХ
        print("\n4. 💾 Тест обработки данных...")
        try:
            processor = DataProcessor(history_size=20)
            test_groups = ["1 2 3 4", "5 6 7 8", "9 10 11 12", "13 14 15 16"]
            features, targets = processor.prepare_training_data(test_groups)
            
            if len(features) > 0:
                print(f"   ✅ Обработано данных: {len(features)} примеров")
                print(f"   📊 Размер features: {features.shape}")
                print(f"   📊 Размер targets: {targets.shape}")
            else:
                print("   ⚠️  Недостаточно данных для создания примеров")
                
        except Exception as e:
            print(f"   ❌ Ошибка обработки данных: {e}")
            return False
        
        # 5. ТЕСТ ПРЕДСКАЗАТЕЛЯ
        print("\n5. 🔮 Тест предсказателя...")
        try:
            predictor = EnhancedPredictor()
            print("   ✅ Предсказатель создан")
            
            # Тест загрузки модели (если существует)
            model_exists = os.path.exists('/opt/dev/data/models/simple_model.pth')
            if model_exists:
                loaded = predictor.load_model()
                if loaded:
                    print("   ✅ Модель загружена")
                else:
                    print("   ⚠️  Модель существует но не загружается")
            else:
                print("   📝 Модель еще не обучена")
                
        except Exception as e:
            print(f"   ❌ Ошибка предсказателя: {e}")
            return False
        
        # 6. ТЕСТ ТРЕНЕРА
        print("\n6. 🧠 Тест тренера...")
        try:
            trainer = EnhancedTrainer()
            print("   ✅ Тренер создан")
            
            # Тест callback системы
            def test_callback(msg):
                print(f"   📢 Callback: {msg}")
            
            trainer.set_progress_callback(test_callback)
            trainer._report_progress("Тестовое сообщение")
            print("   ✅ Callback система работает")
            
        except Exception as e:
            print(f"   ❌ Ошибка тренера: {e}")
            return False
        
        # 7. ТЕСТ УТИЛИТ ДАННЫХ
        print("\n7. 📁 Тест утилит данных...")
        try:
            # Тест валидации
            valid_group = "1 2 3 4"
            invalid_group = "1 2 3"
            
            is_valid = validate_group(valid_group)
            is_invalid = not validate_group(invalid_group)
            
            if is_valid and is_invalid:
                print("   ✅ Валидация групп работает")
            else:
                print("   ❌ Ошибка валидации групп")
                return False
            
            # Тест сравнения групп
            from ml.utils.data_utils import compare_groups
            group1 = (1, 2, 3, 4)
            group2 = (1, 5, 3, 6)
            comparison = compare_groups(group1, group2)
            print(f"   ✅ Сравнение групп: {comparison}")
            
        except Exception as e:
            print(f"   ❌ Ошибка утилит данных: {e}")
            return False
        
        print("\n" + "=" * 60)
        print("🎉 ВСЕ ТЕСТЫ ML ЯДРА ПРОЙДЕНЫ УСПЕШНО!")
        print("✅ ML система готова к работе")
        print("➡️  Можете переходить к ЭТАПУ 3 - САМООБУЧЕНИЕ И АНСАМБЛИ")
        
        return True
        
    except Exception as e:
        print(f"\n❌ КРИТИЧЕСКАЯ ОШИБКА ТЕСТИРОВАНИЯ: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = test_ml_core_system()
    sys.exit(0 if success else 1)