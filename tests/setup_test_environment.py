#[file name]: tests/setup_test_environment.py
#!/usr/bin/env python3
"""
НАСТРОЙКА ТЕСТОВОЙ СРЕДЫ
Создает изолированную тестовую среду без воздействия на рабочие файлы
"""

import os
import sys
import shutil
import json

def setup_test_environment():
    """Создание тестовой среды"""
    print("🎯 НАСТРОЙКА ИЗОЛИРОВАННОЙ ТЕСТОВОЙ СРЕДЫ")
    
    PROJECT_PATH = '/opt/project'
    TEST_BASE_DIR = os.path.join(PROJECT_PATH, 'tests')
    
    # Создаем тестовые директории
    directories = [
        TEST_BASE_DIR,
        os.path.join(TEST_BASE_DIR, 'test_data'),
        os.path.join(TEST_BASE_DIR, 'test_config'),
        os.path.join(TEST_BASE_DIR, 'test_logs')
    ]
    
    for directory in directories:
        os.makedirs(directory, exist_ok=True)
        print(f"✅ Создана директория: {directory}")
    
    # Создаем тестовые файлы
    create_test_files(TEST_BASE_DIR)
    
    print("\n🎉 ТЕСТОВАЯ СРЕДА ГОТОВА!")
    print("📍 Расположение: /opt/project/tests/")
    print("🔒 Полностью изолирована от рабочих файлов")
    print("\n🚀 Для запуска тестов: python3 tests/run_tests.py")

def create_test_files(test_base_dir):
    """Создание тестовых файлов"""
    test_data_dir = os.path.join(test_base_dir, 'test_data')
    test_config_dir = os.path.join(test_base_dir, 'test_config')
    
    # 1. Тестовый dataset.json
    test_dataset = [
        "1 2 3 4", "5 6 7 8", "9 10 11 12", "13 14 15 16",
        "17 18 19 20", "21 22 23 24", "1 3 5 7", "2 4 6 8", 
        "9 11 13 15", "10 12 14 16"
    ]
    
    with open(os.path.join(test_data_dir, 'dataset.json'), 'w', encoding='utf-8') as f:
        json.dump(test_dataset, f, ensure_ascii=False, indent=2)
    print("✅ Создан test_data/dataset.json")
    
    # 2. Тестовый info.json
    test_info = {
        "current_draw": "308826",
        "service_status": "active", 
        "history": [
            {
                "draw": "308826",
                "combination": "17 10 11 18",
                "timestamp": "2024-01-15T12:14:00",
                "processed": True,
                "service_type": "auto_learning"
            },
            {
                "draw": "308825", 
                "combination": "5 12 19 23",
                "timestamp": "2024-01-15T11:59:00",
                "processed": True, 
                "service_type": "web"
            }
        ]
    }
    
    with open(os.path.join(test_data_dir, 'info.json'), 'w', encoding='utf-8') as f:
        json.dump(test_info, f, ensure_ascii=False, indent=2)
    print("✅ Создан test_data/info.json")
    
    # 3. Тестовые прогнозы
    test_predictions = {
        "predictions": [
            {"group": [1, 9, 22, 19], "score": 0.0245},
            {"group": [5, 12, 18, 25], "score": 0.0187},
            {"group": [3, 11, 17, 24], "score": 0.0123},
            {"group": [7, 14, 20, 26], "score": 0.0089}
        ]
    }
    
    with open(os.path.join(test_data_dir, 'predictions_state.json'), 'w', encoding='utf-8') as f:
        json.dump(test_predictions, f, ensure_ascii=False, indent=2)
    print("✅ Создан test_data/predictions_state.json")
    
    # 4. Пустая тестовая модель (копируем структуру если нужно)
    with open(os.path.join(test_data_dir, 'simple_model.pth'), 'w') as f:
        f.write("# TEST MODEL - DO NOT USE IN PRODUCTION\n")
    print("✅ Создан test_data/simple_model.pth")
    
    # 5. Тестовый конфиг Telegram
    test_telegram_config = {
        "enabled": False,
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
    
    with open(os.path.join(test_config_dir, 'telegram_config.json'), 'w', encoding='utf-8') as f:
        json.dump(test_telegram_config, f, ensure_ascii=False, indent=2)
    print("✅ Создан test_config/telegram_config.json")
    
    # 6. Service state файл
    test_service_state = {
        "last_processed_draw": "308826",
        "service_active": True,
        "consecutive_api_errors": 0,
        "last_update": "2024-01-15T12:00:00"
    }
    
    with open(os.path.join(test_data_dir, 'service_state.json'), 'w', encoding='utf-8') as f:
        json.dump(test_service_state, f, ensure_ascii=False, indent=2)
    print("✅ Создан test_data/service_state.json")

if __name__ == "__main__":
    setup_test_environment()