# [file name]: tests/test_auto_learning_service.py (ИСПРАВЛЕННЫЙ)
#!/usr/bin/env python3
"""
ТЕСТЫ автосервиса - упрощенные без сложных импортов
"""

import os
import json
import pytest
from unittest.mock import patch, MagicMock

class TestAutoLearningService:
    """Тесты автосервиса с моками"""
    
    def test_service_initialization(self, mock_simple_system):
        """Тест инициализации сервиса"""
        print("🧪 Тест инициализации сервиса...")
        
        # Импортируем ТОЛЬКО после мокинга
        with patch('api_data.auto_learning_service.schedule'), \
             patch('api_data.auto_learning_service.TelegramNotifier'):
            
            from api_data.auto_learning_service import AutoLearningService
            
            service = AutoLearningService()
            
            assert service.system is not None
            assert service.service_active is True
            print("✅ Сервис инициализирован корректно")
    
    def test_calculate_next_run_time(self):
        """Тест расчета времени следующего запуска"""
        print("🧪 Тест расчета времени запуска...")
        
        with patch('api_data.auto_learning_service.schedule'), \
             patch('api_data.auto_learning_service.TelegramNotifier'), \
             patch('api_data.auto_learning_service.SimpleNeuralSystem'):
            
            from api_data.auto_learning_service import AutoLearningService
            
            service = AutoLearningService()
            
            # Мокаем datetime
            with patch('api_data.auto_learning_service.datetime') as mock_datetime:
                from datetime import datetime
                mock_datetime.now.return_value = datetime(2024, 1, 15, 12, 5, 0)
                
                interval = service.calculate_next_run_time()
                assert interval == 9.0  # 12:05 -> 12:14 = 9 минут
                print(f"✅ Расчет времени корректен: {interval} минут")
    
    def test_telegram_notifier(self):
        """Тест Telegram нотификатора"""
        print("🧪 Тест Telegram нотификатора...")
        
        with patch('api_data.auto_learning_service.requests'):
            from api_data.auto_learning_service import TelegramNotifier
            
            notifier = TelegramNotifier()
            
            # Мокаем конфиг
            notifier.config = {
                'enabled': False,
                'bot_token': 'TEST',
                'chat_id': 'TEST'
            }
            
            # Тестируем отправку сообщения (должен вернуть False т.к. disabled)
            result = notifier.send_message("Test message")
            assert result is False
            print("✅ Telegram нотификатор работает")

def test_info_json_operations():
    """Тест операций с info.json"""
    print("🧪 Тест операций с info.json...")
    
    with patch('api_data.auto_learning_service.schedule'), \
         patch('api_data.auto_learning_service.TelegramNotifier'), \
         patch('api_data.auto_learning_service.SimpleNeuralSystem'):
        
        from api_data.auto_learning_service import AutoLearningService
        
        service = AutoLearningService()
        
        # Тестируем чтение info.json
        info_data = service.get_current_info()
        assert info_data is not None
        assert 'current_draw' in info_data
        print("✅ Операции с info.json работают")

if __name__ == "__main__":
    pytest.main([__file__, '-v'])