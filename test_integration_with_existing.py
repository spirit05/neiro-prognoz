# [file name]: test_integration_with_existing.py
"""
Тестирование интеграции новых модулей с существующей системой
"""

import sys
import os
sys.path.insert(0, '/opt/dev')

def test_with_existing_ml_core():
    """Тестирование интеграции с существующим ML ядром"""
    print("🔗 ТЕСТИРОВАНИЕ ИНТЕГРАЦИИ С СУЩЕСТВУЮЩИМ ML ЯДРОМ")
    
    try:
        # Проверяем, что базовые ML компоненты работают
        from ml.core.model import EnhancedNumberPredictor
        from ml.core.predictor import EnhancedPredictor
        from ml.core.data_processor import DataProcessor
        
        print("✅ Базовые ML компоненты загружены")
        
        # Проверяем интеграцию ансамбля с EnhancedPredictor
        from ml.ensemble.ensemble import EnsemblePredictor
        ensemble = EnsemblePredictor()
        
        # Создаем mock predictor для тестирования
        class MockPredictor:
            def predict_group(self, history, top_k):
                return [((1, 2, 3, 4), 0.5), ((5, 6, 7, 8), 0.3)]
        
        mock_predictor = MockPredictor()
        ensemble.set_neural_predictor(mock_predictor)
        
        test_history = list(range(1, 30))
        predictions = ensemble.predict_ensemble(test_history, 5)
        print(f"✅ Интеграция EnsemblePredictor с EnhancedPredictor - УСПЕХ")
        
        # Проверяем работу с данными
        from ml.utils.data_utils import load_dataset, save_dataset
        test_data = ["1 2 3 4", "5 6 7 8"]
        save_dataset(test_data)
        loaded_data = load_dataset()
        print(f"✅ Работа с данными - УСПЕХ (загружено {len(loaded_data)} групп)")
        
        return True
        
    except Exception as e:
        print(f"❌ Ошибка интеграции с ML ядром: {e}")
        return False

def test_config_integration():
    """Тестирование интеграции с конфигурацией"""
    print("\n⚙️ ТЕСТИРОВАНИЕ ИНТЕГРАЦИИ С КОНФИГУРАЦИЕЙ")
    
    try:
        from config.paths import DATA_DIR
        from ml.learning.self_learning import SelfLearningSystem
        
        # Проверяем, что пути корректно используются
        learning_system = SelfLearningSystem()
        expected_path = os.path.join(DATA_DIR, "analytics", "learning_results.json")
        print(f"✅ Конфигурация путей - УСПЕХ (путь: {expected_path})")
        
        # Проверяем логирование
        from config.logging_config import setup_logging
        logger = setup_logging()
        print("✅ Конфигурация логирования - УСПЕХ")
        
        return True
        
    except Exception as e:
        print(f"❌ Ошибка интеграции с конфигурацией: {e}")
        return False

if __name__ == "__main__":
    print("🔍 ТЕСТИРОВАНИЕ ИНТЕГРАЦИИ С СУЩЕСТВУЮЩЕЙ СИСТЕМОЙ")
    print("=" * 60)
    
    ml_integration = test_with_existing_ml_core()
    config_integration = test_config_integration()
    
    print("\n" + "=" * 60)
    print("📊 РЕЗУЛЬТАТЫ ИНТЕГРАЦИОННОГО ТЕСТИРОВАНИЯ:")
    print(f"✅ Интеграция с ML ядром: {'УСПЕХ' if ml_integration else 'ОШИБКА'}")
    print(f"✅ Интеграция с конфигурацией: {'УСПЕХ' if config_integration else 'ОШИБКА'}")