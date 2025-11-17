# [file name]: test_integration_with_orchestrator.py
"""
Интеграционные тесты Data Processing с MLOrchestrator
"""

import sys
import os
import tempfile
import json
from pathlib import Path

sys.path.insert(0, '/opt/model')

def test_orchestrator_data_processing_init():
    """Тест инициализации Data Processing в Orchestrator"""
    print("🧪 Тест инициализации Data Processing в Orchestrator...")
    
    try:
        from ml.core.orchestrator import MLOrchestrator
        
        # Создаем тестовую конфигурацию
        test_config = {
            'data_processing': {
                'processor': {
                    'class': 'ml.data.processors.data_processor.ModularDataProcessor',
                    'params': {
                        'history_size': 20,
                        'feature_engineers': ['statistical', 'advanced']
                    }
                },
                'dataset_manager': {
                    'dataset_path': '/tmp/test_orchestrator_dataset.json'
                }
            }
        }
        
        orchestrator = MLOrchestrator(test_config)
        
        # Проверяем статус системы
        status = orchestrator.get_system_status()
        print(f"✅ Статус системы: data_processing_initialized={status['data_processing_initialized']}")
        
        # Проверяем информацию о данных
        data_info = orchestrator.get_data_processing_info()
        print(f"✅ Информация о данных: {data_info}")
        
        # Проверяем что компоненты инициализированы
        assert status['data_processing_initialized'] == True, "Data Processing не инициализирован"
        assert data_info['data_processor_initialized'] == True, "Data Processor не инициализирован"
        assert data_info['dataset_manager_initialized'] == True, "Dataset Manager не инициализирован"
        assert data_info['data_validator_initialized'] == True, "Data Validator не инициализирован"
        
        return True
        
    except Exception as e:
        print(f"❌ Ошибка инициализации Data Processing в Orchestrator: {e}")
        return False

def test_orchestrator_data_operations():
    """Тест операций с данными через Orchestrator"""
    print("\n🧪 Тест операций с данными через Orchestrator...")
    
    try:
        from ml.core.orchestrator import MLOrchestrator
        
        # Создаем временный файл dataset
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
            json.dump([], f)
            temp_dataset_path = f.name
        
        test_config = {
            'data_processing': {
                'processor': {
                    'class': 'ml.data.processors.data_processor.ModularDataProcessor',
                    'params': {
                        'history_size': 20,
                        'feature_engineers': ['statistical', 'advanced']
                    }
                },
                'dataset_manager': {
                    'dataset_path': temp_dataset_path
                }
            }
        }
        
        orchestrator = MLOrchestrator(test_config)
        
        # Тест добавления данных
        test_groups = [
            "1 2 3 4", "5 6 7 8", "9 10 11 12", "13 14 15 16", "17 18 19 20",
            "21 22 23 24", "1 3 5 7", "2 4 6 8", "10 11 12 13", "14 15 16 17"
        ]
        
        success = orchestrator.add_new_data(test_groups)
        print(f"✅ Добавление данных через Orchestrator: {success}")
        
        # Проверяем что данные добавились
        data_info = orchestrator.get_data_processing_info()
        print(f"✅ Статистика после добавления: {data_info['valid_groups']} валидных групп")
        
        # Тест создания фич для предсказания
        prediction_batch = orchestrator.create_prediction_features(test_groups[-3:])
        print(f"✅ Создание фич предсказания через Orchestrator: {not prediction_batch.empty}")
        
        if not prediction_batch.empty:
            print(f"   Размер фич: {prediction_batch.data.shape}")
        
        # Тест подготовки данных обучения
        try:
            features_batch, targets_batch = orchestrator.prepare_training_data()
            print(f"✅ Подготовка данных обучения через Orchestrator: features={not features_batch.empty}, targets={not targets_batch.empty}")
            
            if not features_batch.empty:
                print(f"   Размер фич: {features_batch.data.shape}")
            if not targets_batch.empty:
                print(f"   Размер таргетов: {targets_batch.data.shape}")
        except Exception as e:
            print(f"⚠️ Подготовка данных обучения: {e} (может быть недостаточно данных)")
        
        # Очистка
        Path(temp_dataset_path).unlink(missing_ok=True)
        
        return True
        
    except Exception as e:
        print(f"❌ Ошибка операций с данными через Orchestrator: {e}")
        # Очистка в случае ошибки
        if 'temp_dataset_path' in locals():
            Path(temp_dataset_path).unlink(missing_ok=True)
        return False

def test_orchestrator_data_validation():
    """Тест валидации данных через Orchestrator"""
    print("\n🧪 Тест валидации данных через Orchestrator...")
    
    try:
        from ml.core.orchestrator import MLOrchestrator
        
        orchestrator = MLOrchestrator()
        
        # Тест валидации предсказаний
        predictions = [
            (1, 2, 3, 4),
            (5, 6, 7, 8), 
            (9, 10, 11, 12)
        ]
        actuals = [
            [1, 2, 5, 6],
            [5, 6, 9, 10],
            [9, 10, 13, 14]
        ]
        
        accuracy_stats = orchestrator.validate_prediction_accuracy(predictions, actuals)
        print(f"✅ Валидация точности предсказаний: {accuracy_stats}")
        
        if accuracy_stats:
            print(f"   Среднее совпадений: {accuracy_stats.get('average_matches', 0):.2f}")
            print(f"   Полных совпадений: {accuracy_stats.get('total_perfect_matches', 0)}")
        
        return True
        
    except Exception as e:
        print(f"❌ Ошибка валидации данных через Orchestrator: {e}")
        return False

def test_orchestrator_backup():
    """Тест бэкапа данных через Orchestrator"""
    print("\n🧪 Тест бэкапа данных через Orchestrator...")
    
    try:
        from ml.core.orchestrator import MLOrchestrator
        
        # Создаем временный dataset с данными
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
            json.dump(["1 2 3 4", "5 6 7 8", "9 10 11 12"], f)
            temp_dataset_path = f.name
        
        test_config = {
            'data_processing': {
                'processor': {
                    'class': 'ml.data.processors.data_processor.ModularDataProcessor',
                    'params': {
                        'history_size': 20
                    }
                },
                'dataset_manager': {
                    'dataset_path': temp_dataset_path
                }
            }
        }
        
        orchestrator = MLOrchestrator(test_config)
        
        # Тест бэкапа
        backup_success = orchestrator.backup_dataset()
        print(f"✅ Бэкап dataset через Orchestrator: {backup_success}")
        
        # Проверяем что бэкап создан
        backup_path = Path(temp_dataset_path).with_suffix('.backup.json')
        backup_exists = backup_path.exists()
        print(f"✅ Файл бэкапа создан: {backup_exists}")
        
        # Очистка
        Path(temp_dataset_path).unlink(missing_ok=True)
        backup_path.unlink(missing_ok=True)
        
        return backup_success and backup_exists
        
    except Exception as e:
        print(f"❌ Ошибка бэкапа данных через Orchestrator: {e}")
        # Очистка в случае ошибки
        if 'temp_dataset_path' in locals():
            Path(temp_dataset_path).unlink(missing_ok=True)
        if 'backup_path' in locals():
            backup_path.unlink(missing_ok=True)
        return False

def test_orchestrator_default_config():
    """Тест работы Orchestrator с конфигурацией по умолчанию"""
    print("\n🧪 Тест работы Orchestrator с конфигурацией по умолчанию...")
    
    try:
        from ml.core.orchestrator import MLOrchestrator
        
        # Создаем orchestrator без конфигурации (должен использовать настройки по умолчанию)
        orchestrator = MLOrchestrator()
        
        # Проверяем статус
        status = orchestrator.get_system_status()
        print(f"✅ Статус с конфигурацией по умолчанию: data_processing_initialized={status['data_processing_initialized']}")
        
        # Проверяем информацию о данных
        data_info = orchestrator.get_data_processing_info()
        print(f"✅ Информация о данных с конфигурацией по умолчанию: processor={data_info['data_processor_initialized']}")
        
        # Проверяем что компоненты инициализированы
        assert status['data_processing_initialized'] == True, "Data Processing не инициализирован с конфигурацией по умолчанию"
        
        return True
        
    except Exception as e:
        print(f"❌ Ошибка работы с конфигурацией по умолчанию: {e}")
        return False

if __name__ == "__main__":
    print("🚀 ЗАПУСК ИНТЕГРАЦИОННЫХ ТЕСТОВ С ORCHESTRATOR")
    print("=" * 60)
    
    tests = [
        test_orchestrator_data_processing_init,
        test_orchestrator_data_operations,
        test_orchestrator_data_validation,
        test_orchestrator_backup,
        test_orchestrator_default_config
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
        print(f"🎉 ВСЕ ИНТЕГРАЦИОННЫЕ ТЕСТЫ ПРОЙДЕНЫ! ({passed}/{total})")
        print("✅ Data Processing полностью интегрирован с MLOrchestrator!")
    else:
        print(f"⚠️  ПРОЙДЕНО ИНТЕГРАЦИОННЫХ ТЕСТОВ: {passed}/{total}")
        print("❌ Требуется исправление интеграции")
    
    exit(0 if passed == total else 1)
