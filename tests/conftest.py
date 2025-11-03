#[file name]: tests/conftest.py
#!/usr/bin/env python3
"""
Конфигурация тестовой среды - изоляция от рабочих файлов
"""

import os
import sys
import tempfile
import shutil
import json
from unittest.mock import patch
import pytest

# Добавляем пути для импорта
PROJECT_PATH = '/opt/project'
sys.path.insert(0, PROJECT_PATH)
sys.path.insert(0, os.path.join(PROJECT_PATH, 'model'))
sys.path.insert(0, os.path.dirname(__file__))

# Тестовые пути
TEST_BASE_DIR = os.path.join(PROJECT_PATH, 'tests')
TEST_DATA_DIR = os.path.join(TEST_BASE_DIR, 'test_data')
TEST_CONFIG_DIR = os.path.join(TEST_BASE_DIR, 'test_config') 
TEST_LOGS_DIR = os.path.join(TEST_BASE_DIR, 'test_logs')

@pytest.fixture(scope='session', autouse=True)
def setup_test_environment():
    """Создание тестовой среды перед всеми тестами"""
    print("\n🧪 НАСТРОЙКА ТЕСТОВОЙ СРЕДЫ...")
    
    # Создаем тестовые директории
    os.makedirs(TEST_DATA_DIR, exist_ok=True)
    os.makedirs(TEST_CONFIG_DIR, exist_ok=True)
    os.makedirs(TEST_LOGS_DIR, exist_ok=True)
    
    # Создаем тестовые файлы данных
    create_test_dataset()
    create_test_info_json()
    create_test_predictions()
    create_test_telegram_config()
    
    print("✅ Тестовая среда готова")
    
    yield
    
    # Очистка после тестов (опционально)
    # print("\n🧹 ОЧИСТКА ТЕСТОВОЙ СРЕДЫ...")
    # shutil.rmtree(TEST_DATA_DIR, ignore_errors=True)
    # shutil.rmtree(TEST_LOGS_DIR, ignore_errors=True)

def create_test_dataset():
    """Создание тестового dataset.json"""
    test_data = [
        "1 2 3 4", "5 6 7 8", "9 10 11 12", "13 14 15 16",
        "17 18 19 20", "21 22 23 24", "1 3 5 7", "2 4 6 8",
        "9 11 13 15", "10 12 14 16"
    ]
    
    dataset_path = os.path.join(TEST_DATA_DIR, 'dataset.json')
    with open(dataset_path, 'w', encoding='utf-8') as f:
        json.dump(test_data, f, ensure_ascii=False, indent=2)

def create_test_info_json():
    """Создание тестового info.json"""
    test_info = {
        "current_draw": "308826",
        "service_status": "active",
        "history": [
            {
                "draw": "308826",
                "combination": "17 10 11 18",
                "timestamp": "2024-01-15T12:14:00",
                "processed": True,
                "service_type": "auto_learning",
                "processing_time": "2024-01-15T12:15:23"
            },
            {
                "draw": "308825",
                "combination": "5 12 19 23",
                "timestamp": "2024-01-15T11:59:00", 
                "processed": True,
                "service_type": "web",
                "processing_time": "2024-01-15T12:00:15"
            }
        ]
    }
    
    info_path = os.path.join(TEST_DATA_DIR, 'info.json')
    with open(info_path, 'w', encoding='utf-8') as f:
        json.dump(test_info, f, ensure_ascii=False, indent=2)

def create_test_predictions():
    """Создание тестовых прогнозов"""
    test_predictions = {
        "predictions": [
            {"group": [1, 9, 22, 19], "score": 0.0245},
            {"group": [5, 12, 18, 25], "score": 0.0187},
            {"group": [3, 11, 17, 24], "score": 0.0123},
            {"group": [7, 14, 20, 26], "score": 0.0089}
        ]
    }
    
    predictions_path = os.path.join(TEST_DATA_DIR, 'predictions_state.json')
    with open(predictions_path, 'w', encoding='utf-8') as f:
        json.dump(test_predictions, f, ensure_ascii=False, indent=2)

def create_test_telegram_config():
    """Создание тестового конфига Telegram"""
    test_config = {
        "enabled": False,  # В тестах отключаем реальные уведомления
        "bot_token": "TEST_BOT_TOKEN",
        "chat_id": "TEST_CHAT_ID",
        "notifications": {
            "critical_errors": True,
            "all_errors": True, 
            "service_stop": True,
            "predictions": False,
            "status_command": True
        }
    }
    
    config_path = os.path.join(TEST_CONFIG_DIR, 'telegram_config.json')
    with open(config_path, 'w', encoding='utf-8') as f:
        json.dump(test_config, f, ensure_ascii=False, indent=2)

@pytest.fixture
def mock_paths():
    """Фикстура для подмены путей на тестовые"""
    
    # Патчим пути в data_loader
    with patch('model.data_loader.DATA_DIR', TEST_DATA_DIR), \
         patch('model.data_loader.DATASET_PATH', os.path.join(TEST_DATA_DIR, 'dataset.json')), \
         patch('model.data_loader.STATE_PATH', os.path.join(TEST_DATA_DIR, 'predictions_state.json')), \
         patch('api_data.auto_learning_service.PROJECT_PATH', PROJECT_PATH), \
         patch('api_data.auto_learning_service.TELEGRAM_CONFIG_FILE', os.path.join(TEST_CONFIG_DIR, 'telegram_config.json')), \
         patch('api_data.auto_learning_service.SERVICE_STATE_FILE', os.path.join(TEST_DATA_DIR, 'service_state.json')), \
         patch('api_data.get_group.DATA_DIR', TEST_DATA_DIR), \
         patch('api_data.get_group.STATE_PATH', os.path.join(TEST_DATA_DIR, 'info.json')):
        
        yield

@pytest.fixture
def mock_api_call():
    """Фикстура для мокирования API вызовов"""
    def mock_get_data_with_curl():
        # Возвращаем mock данные вместо реального API вызова
        return {
            'combination': {
                'structured': [17, 10, 11, 18]
            }
        }
    
    with patch('api_data.auto_learning_service.get_data_with_curl', mock_get_data_with_curl), \
         patch('api_data.get_group.get_data_with_curl', mock_get_data_with_curl):
        yield