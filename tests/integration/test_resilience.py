# tests/integration/test_resilience.py
"""
ТЕСТЫ УСТОЙЧИВОСТИ - восстановление после сбоев
"""
from unittest.mock import patch, MagicMock

def test_api_failure_recovery():
    """Тест восстановления после сбоев API"""
    print("🧪 Тест восстановления после сбоев API...")
    
    with patch('api_data.auto_learning_service.subprocess') as mock_subprocess, \
         patch('api_data.auto_learning_service.SimpleNeuralSystem'):
        
        # Мокаем сбой API
        mock_subprocess.run.side_effect = [
            Exception("API timeout"),  # Первая попытка - сбой
            Exception("API timeout"),  # Вторая попытка - сбой  
            MagicMock(returncode=0, stdout='{"combination": {"structured": [1,2,3,4]}}')  # Успех
        ]
        
        from auto_learning_service import AutoLearningService
        
        service = AutoLearningService()
        service.consecutive_api_errors = 0
        
        # Должно восстановиться после 2 ошибок
        result = service.call_api_with_retries()
        assert result is not None
        print("✅ Система восстановилась после сбоев API")