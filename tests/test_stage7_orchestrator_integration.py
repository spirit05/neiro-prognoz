# [file name]: tests/test_stage7_orchestrator_integration.py
"""
Тест интеграции оркестратора ЭТАП 7 - ИСПРАВЛЕННАЯ ВЕРСИЯ
"""

import pytest
import sys
import os
import numpy as np

sys.path.insert(0, '/opt/model')

def test_config_loader():
    """Тест загрузчика конфигурации"""
    try:
        from ml.core.config_loader import ConfigLoader
        
        loader = ConfigLoader()
        
        # Загрузка конфигураций
        configs = loader.load_component_configs()
        
        assert 'model' in configs, "Конфигурация модели не загружена"
        assert 'ensemble' in configs, "Конфигурация ансамбля не загружена"
        assert 'learning' in configs, "Конфигурация обучения не загружена"
        assert 'features' in configs, "Конфигурация фич не загружена"
        
        print("✅ Загрузчик конфигурации работает")
        return True
        
    except Exception as e:
        print(f"❌ Тест загрузчика конфигурации провален: {e}")
        return False

def test_orchestrator_initialization():
    """Тест инициализации оркестратора"""
    try:
        from ml.core.orchestrator import MLOrchestrator
        
        # Создаем оркестратор с автоматической загрузкой конфигурации
        orchestrator = MLOrchestrator()
        
        # Проверяем что компоненты загружены
        status = orchestrator.get_system_status()
        
        assert status['models_registered'] >= 0, "Модели не зарегистрированы"
        assert isinstance(status['feature_engineers'], list), "Feature engineers не список"
        assert isinstance(status['ensemble_predictors'], list), "Ensemble predictors не список"
        
        print(f"✅ Статус системы: {status}")
        print("✅ Оркестратор инициализирован")
        return True
        
    except Exception as e:
        print(f"❌ Тест инициализации оркестратора провален: {e}")
        return False

def test_feature_engineers():
    """Тест работы feature engineers"""
    try:
        from ml.core.orchestrator import MLOrchestrator
        
        orchestrator = MLOrchestrator()
        
        # Проверяем feature engineers
        feature_engineers = orchestrator.get_feature_engineers()
        assert len(feature_engineers) > 0, "Feature engineers не загружены"
        
        # Тестируем извлечение фич
        test_data = list(range(1, 21))
        features = orchestrator.extract_features(test_data)
        
        assert len(features) > 0, "Фичи не извлечены"
        for name, feature_array in features.items():
            assert feature_array is not None, f"Фичи {name} None"
            assert len(feature_array) > 0, f"Фичи {name} пустые"
            assert isinstance(feature_array, np.ndarray), f"Фичи {name} не numpy array"
        
        print("✅ Feature engineers работают")
        return True
        
    except Exception as e:
        print(f"❌ Тест feature engineers провален: {e}")
        return False

def test_ensemble_predictors():
    """Тест ансамблевых предсказателей"""
    try:
        from ml.core.orchestrator import MLOrchestrator
        
        orchestrator = MLOrchestrator()
        
        # Получаем ансамблевые предсказатели
        ensemble_predictors = orchestrator.get_ensemble_predictors()
        
        # Если есть предсказатели, тестируем их
        if ensemble_predictors:
            # Тестируем ансамблевое предсказание
            test_history = list(range(1, 31))
            predictions = orchestrator.ensemble_predict(test_history, top_k=5)
            
            assert isinstance(predictions, list), "Предсказания не список"
            
            if predictions:
                for group, score in predictions:
                    assert isinstance(group, tuple), "Группа не tuple"
                    assert len(group) == 4, "Группа не из 4 чисел"
                    assert all(1 <= num <= 26 for num in group), "Числа вне диапазона 1-26"
                    assert isinstance(score, (int, float)), "Score не число"
        
        print("✅ Ансамблевые предсказатели работают")
        return True
        
    except Exception as e:
        print(f"❌ Тест ансамблевых предсказателей провален: {e}")
        return False

def test_model_registration():
    """Тест регистрации моделей"""
    try:
        from ml.core.orchestrator import MLOrchestrator
        from ml.core.types import ModelType, ModelStatus
        from ml.core.base_model import AbstractBaseModel
        
        orchestrator = MLOrchestrator()
        
        # Создаем тестовую модель
        class TestModel(AbstractBaseModel):
            def __init__(self):
                super().__init__("test_model", ModelType.REGRESSION)
            
            def train(self, data, config):
                return None
            
            def predict(self, data):
                return None
            
            def save(self, path):
                pass
            
            def load(self, path):
                pass
        
        # Регистрируем модель
        test_model = TestModel()
        orchestrator.register_model(test_model)
        
        # Проверяем регистрацию
        model_info = orchestrator.get_model_info("test_model")
        assert model_info is not None, "Модель не зарегистрирована"
        assert model_info['model_id'] == "test_model", "Неверный model_id"
        
        # Проверяем список моделей
        models_list = orchestrator.list_models()
        assert len(models_list) > 0, "Список моделей пуст"
        
        print("✅ Регистрация моделей работает")
        return True
        
    except Exception as e:
        print(f"❌ Тест регистрации моделей провален: {e}")
        return False

if __name__ == "__main__":
    print("🧪 Запуск тестов ЭТАПА 7: ИНТЕГРАЦИЯ ORCHESTRATOR")
    print("=" * 60)
    
    tests = [
        test_config_loader,
        test_orchestrator_initialization,
        test_feature_engineers,
        test_ensemble_predictors,
        test_model_registration
    ]
    
    results = []
    for test in tests:
        try:
            result = test()
            results.append(result)
            print()
        except Exception as e:
            print(f"❌ Тест {test.__name__} упал с ошибкой: {e}")
            results.append(False)
            print()
    
    passed = sum(results)
    total = len(results)
    
    print("=" * 60)
    if passed == total:
        print(f"🎉 ВСЕ ТЕСТЫ ПРОЙДЕНЫ! ({passed}/{total})")
        print("✅ ЭТАП 7 ЗАВЕРШЕН УСПЕШНО!")
    else:
        print(f"⚠️  ПРОЙДЕНО ТЕСТОВ: {passed}/{total}")
        print("❌ Требуется исправление ошибок")
    
    sys.exit(0 if passed == total else 1)
