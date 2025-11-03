#[file name]: tests/test_safe_operations.py
#!/usr/bin/env python3
"""
ТЕСТЫ безопасных операций и изоляции
"""

import os
import json
import pytest
from unittest.mock import patch

def test_environment_isolation():
    """Тест что тестовая среда изолирована от рабочих файлов"""
    print("🧪 Тест изоляции среды...")
    
    # Проверяем что тестовые файлы существуют
    test_files = [
        '/opt/project/tests/test_data/dataset.json',
        '/opt/project/tests/test_data/info.json', 
        '/opt/project/tests/test_data/predictions_state.json',
        '/opt/project/tests/test_config/telegram_config.json'
    ]
    
    for file_path in test_files:
        assert os.path.exists(file_path), f"Тестовый файл {file_path} не найден"
    
    # Проверяем что рабочие файлы НЕ используются в тестах
    with patch('model.data_loader.DATA_DIR', '/opt/project/tests/test_data'):
        from model.data_loader import DATASET_PATH
        assert DATASET_PATH.startswith('/opt/project/tests/'), "Используются рабочие пути!"
    
    print("✅ Тестовая среда полностью изолирована")

def test_test_files_content():
    """Тест содержимого тестовых файлов"""
    print("🧪 Тест содержимого тестовых файлов...")
    
    # Проверяем dataset.json
    with open('/opt/project/tests/test_data/dataset.json', 'r') as f:
        dataset = json.load(f)
        assert isinstance(dataset, list)
        assert len(dataset) == 10
        print("✅ dataset.json корректен")
    
    # Проверяем info.json
    with open('/opt/project/tests/test_data/info.json', 'r') as f:
        info = json.load(f)
        assert 'current_draw' in info
        assert 'history' in info
        assert len(info['history']) == 2
        print("✅ info.json корректен")
    
    # Проверяем predictions
    with open('/opt/project/tests/test_data/predictions_state.json', 'r') as f:
        predictions = json.load(f)
        assert 'predictions' in predictions
        assert len(predictions['predictions']) == 4
        print("✅ predictions_state.json корректен")

def test_no_impact_on_production():
    """Тест что тесты не затрагивают продакшен файлы"""
    print("🧪 Тест отсутствия воздействия на продакшен...")
    
    production_files = [
        '/opt/project/data/dataset.json',
        '/opt/project/data/predictions_state.json', 
        '/opt/project/data/simple_model.pth',
        '/opt/project/api_data/info.json'
    ]
    
    # Сохраняем временные метки файлов
    original_timestamps = {}
    for file_path in production_files:
        if os.path.exists(file_path):
            original_timestamps[file_path] = os.path.getmtime(file_path)
    
    # Запускаем тесты
    from tests.test_auto_learning_service import TestAutoLearningService
    test_class = TestAutoLearningService()
    
    with patch('tests.test_auto_learning_service.mock_paths'):
        test_class.test_service_initialization()
        test_class.test_service_status()
    
    # Проверяем что файлы не изменились
    for file_path, original_timestamp in original_timestamps.items():
        if os.path.exists(file_path):
            current_timestamp = os.path.getmtime(file_path)
            assert current_timestamp == original_timestamp, f"Файл {file_path} был изменен тестами!"
    
    print("✅ Продакшен файлы не затронуты тестами")

if __name__ == "__main__":
    pytest.main([__file__, '-v'])