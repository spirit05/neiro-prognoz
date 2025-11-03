# tests/integration/test_real_workflow.py
"""
ТЕСТЫ РЕАЛЬНОГО WORKFLOW - полный цикл работы системы
"""
import os
import json
from unittest.mock import patch, MagicMock

def test_complete_workflow():
    """Тест полного цикла: API → Обработка → Обучение → Прогнозы"""
    print("🧪 Тест полного workflow...")
    
    # Мокаем все внешние зависимости
    with patch('api_data.auto_learning_service.requests') as mock_requests, \
         patch('api_data.auto_learning_service.subprocess') as mock_subprocess, \
         patch('api_data.auto_learning_service.SimpleNeuralSystem') as mock_system:
        
        # Настраиваем моки
        mock_system_instance = MagicMock()
        mock_system_instance.is_trained = True
        mock_system_instance.add_data_and_retrain.return_value = [
            ((1, 9, 22, 19), 0.0245),
            ((5, 12, 18, 25), 0.0187)
        ]
        mock_system.return_value = mock_system_instance
        
        # Мокаем API ответ
        mock_api_response = {
            'combination': {'structured': [17, 10, 11, 18]}
        }
        mock_subprocess.run.return_value.stdout = json.dumps(mock_api_response)
        mock_subprocess.run.return_value.returncode = 0
        
        # Импортируем и тестируем
        from auto_learning_service import AutoLearningService
        
        service = AutoLearningService()
        service.system = mock_system_instance
        
        # Тестируем обработку новой группы
        result = service.process_new_group()
        
        assert result is True
        print("✅ Полный workflow работает корректно")