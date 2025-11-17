# [file name]: tests/test_stage8_data_processing.py
"""
ИСПРАВЛЕННЫЕ ТЕСТЫ ЭТАПА 8 - Data Processing интеграция
"""

import pytest
import sys
import os
import tempfile
import json
from pathlib import Path

sys.path.insert(0, '/opt/model')

class TestDataProcessingIntegration:
    """Тесты интеграции Data Processing модуля"""
    
    def test_data_processor_functionality(self):
        """Тест базовой функциональности DataProcessor"""
        from ml.data.processors.data_processor import ModularDataProcessor
        
        processor = ModularDataProcessor(history_size=20)
        
        # Тест извлечения фич
        test_history = list(range(1, 21))
        features = processor.extract_features(test_history)
        
        assert 'statistical' in features
        assert 'advanced' in features
        assert len(features['statistical']) == 50
        assert len(features['advanced']) == 15
        
        # Тест информации о фичах
        feature_info = processor.get_feature_info()
        assert feature_info['history_size'] == 20
        assert 'statistical' in feature_info['active_engineers']
    
    def test_dataset_manager_operations(self):
        """Тест операций DatasetManager"""
        from ml.data.providers.dataset_manager import DatasetManager
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
            temp_path = f.name
        
        try:
            manager = DatasetManager(temp_path)
            
            # Тест сохранения и загрузки
            test_data = ["1 2 3 4", "5 6 7 8", "9 10 11 12"]
            assert manager.save_dataset(test_data) == True
            
            loaded_data = manager.load_dataset()
            assert len(loaded_data) == 3
            
            # Тест добавления групп
            new_groups = ["13 14 15 16", "17 18 19 20"]
            assert manager.add_groups(new_groups) == True
            
            # Тест статистики
            stats = manager.get_dataset_stats()
            assert stats['valid_groups'] == 5
            
        finally:
            Path(temp_path).unlink(missing_ok=True)
    
    def test_data_validation(self):
        """Тест валидации данных"""
        from ml.data.quality.validators import DataValidator
        
        validator = DataValidator()
        
        # Тест валидации групп
        assert validator.validate_group("1 2 3 4") == True
        assert validator.validate_group("1 1 3 4") == False
        assert validator.validate_group("1 2 3") == False
        
        # Тест сравнения групп
        comparison = validator.compare_groups((1, 2, 3, 4), (1, 2, 5, 6))
        assert comparison['total_matches'] == 2
        assert comparison['exact_matches'] == 2
    
    def test_orchestrator_integration(self):
        """Тест интеграции с MLOrchestrator"""
        from ml.core.orchestrator import MLOrchestrator
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
            json.dump([], f)
            temp_path = f.name
        
        try:
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
                        'dataset_path': temp_path
                    }
                }
            }
            
            orchestrator = MLOrchestrator(test_config)
            
            # Проверяем инициализацию
            status = orchestrator.get_system_status()
            assert status['data_processing_initialized'] == True
            
            data_info = orchestrator.get_data_processing_info()
            assert data_info['data_processor_initialized'] == True
            assert data_info['dataset_manager_initialized'] == True
            
        finally:
            Path(temp_path).unlink(missing_ok=True)
    
 
    def test_complete_data_workflow(self):
        """Тест полного workflow обработки данных"""
        from ml.core.orchestrator import MLOrchestrator

        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
            json.dump([], f)
            temp_path = f.name

        try:
            test_config = {
                'data_processing': {
                    'processor': {
                        'class': 'ml.data.processors.data_processor.ModularDataProcessor',
                        'params': {'history_size': 20}
                    },
                    'dataset_manager': {'dataset_path': temp_path}
                }
            }

            orchestrator = MLOrchestrator(test_config)

            # Добавляем достаточное количество данных
            test_groups = [
                "1 2 3 4", "5 6 7 8", "9 10 11 12", "13 14 15 16", "17 18 19 20",
                "21 22 23 24", "1 3 5 7", "2 4 6 8", "10 11 12 13", "14 15 16 17",
                "18 19 20 21", "22 23 24 25", "1 2 4 5", "3 6 7 8", "9 11 13 15"
            ]

            # Тест добавления данных
            success = orchestrator.add_new_data(test_groups)
            assert success == True

            # Тест создания фич для предсказания (используем достаточно групп)
            prediction_batch = orchestrator.create_prediction_features(test_groups[-5:])  # 5 групп = 20 чисел
            assert prediction_batch.data.empty == False  # ИСПРАВЛЕНО: используем prediction_batch.data.empty

            # Тест валидации предсказаний
            predictions = [(1, 2, 3, 4), (5, 6, 7, 8)]
            actuals = [[1, 2, 5, 6], [5, 6, 9, 10]]

            accuracy_stats = orchestrator.validate_prediction_accuracy(predictions, actuals)
            assert accuracy_stats['total_comparisons'] == 2

            # Тест бэкапа
            backup_success = orchestrator.backup_dataset()
            assert backup_success == True

        finally:
            Path(temp_path).unlink(missing_ok=True)
            Path(temp_path).with_suffix('.backup.json').unlink(missing_ok=True)
