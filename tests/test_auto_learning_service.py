#[file name]: tests/test_auto_learning_service.py
#!/usr/bin/env python3
"""
ТЕСТЫ автосервиса в изолированной среде
"""

import os
import json
import pytest
from unittest.mock import patch, MagicMock

from api_data.auto_learning_service import AutoLearningService, TelegramNotifier

class TestAutoLearningService:
    """Тесты автосервиса"""
    
    def test_service_initialization(self, mock_paths):
        """Тест инициализации сервиса"""
        print("🧪 Тест инициализации сервиса...")
        
        service = AutoLearningService()
        
        assert service.system is not None
        assert service.service_active is True
        assert service.consecutive_api_errors == 0
        print("✅ Сервис инициализирован корректно")
    
    def test_calculate_next_run_time(self, mock_paths):
        """Тест расчета времени следующего запуска"""
        print("🧪 Тест расчета времени запуска...")
        
        service = AutoLearningService()
        
        # Тестируем с разным временем
        test_cases = [
            (12, 5, 9.0),   # 12:05 -> до 12:14 = 9 минут
            (12, 11, 8.0),  # 12:11 -> до 12:14 = 3 + 5 буфер = 8 минут  
            (12, 13, 6.0),  # 12:13 -> до 12:14 = 1 + 5 буфер = 6 минут
        ]
        
        for hour, minute, expected in test_cases:
            with patch('api_data.auto_learning_service.datetime') as mock_datetime:
                from datetime import datetime
                mock_datetime.now.return_value = datetime(2024, 1, 15, hour, minute, 0)
                mock_datetime.side_effect = lambda *args, **kw: datetime(*args, **kw)
                
                interval = service.calculate_next_run_time()
                assert interval == expected
                print(f"✅ {hour:02d}:{minute:02d} -> интервал {interval} минут")
    
    def test_telegram_notifier_initialization(self):
        """Тест инициализации Telegram нотификатора"""
        print("🧪 Тест Telegram нотификатора...")
        
        notifier = TelegramNotifier()
        
        assert notifier.config is not None
        assert notifier.config.get('enabled') is False  # В тестах отключено
        print("✅ Telegram нотификатор инициализирован")
    
    def test_info_json_operations(self, mock_paths):
        """Тест операций с info.json"""
        print("🧪 Тест операций с info.json...")
        
        service = AutoLearningService()
        
        # Чтение info.json
        info_data = service.get_current_info()
        assert info_data is not None
        assert 'current_draw' in info_data
        assert 'history' in info_data
        print("✅ Чтение info.json работает")
        
        # Проверяем что файл в тестовой директории
        test_info_path = os.path.join('/opt/project/tests/test_data', 'info.json')
        assert os.path.exists(test_info_path)
        print("✅ Файл в тестовой директории")
    
    def test_service_status(self, mock_paths):
        """Тест получения статуса сервиса"""
        print("🧪 Тест получения статуса...")
        
        service = AutoLearningService()
        status = service.get_service_status()
        
        assert 'service_active' in status
        assert 'system_initialized' in status
        assert 'model_trained' in status
        assert 'web_running' in status
        print("✅ Статус сервиса получается корректно")
    
    def test_manual_restart(self, mock_paths):
        """Тест ручного перезапуска"""
        print("🧪 Тест ручного перезапуска...")
        
        service = AutoLearningService()
        service.service_active = False  # Имитируем остановку
        
        result = service.manual_restart()
        
        assert result is True
        assert service.service_active is True
        assert service.consecutive_api_errors == 0
        print("✅ Ручной перезапуск работает")

class TestIntegration:
    """Интеграционные тесты"""
    
    def test_full_processing_cycle(self, mock_paths, mock_api_call):
        """Тест полного цикла обработки"""
        print("🧪 Тест полного цикла обработки...")
        
        service = AutoLearningService()
        
        # Мокаем системные вызовы чтобы избежать реального обучения
        with patch.object(service.system, 'add_data_and_retrain') as mock_retrain:
            mock_retrain.return_value = [
                ((1, 9, 22, 19), 0.0245),
                ((5, 12, 18, 25), 0.0187)
            ]
            
            # Запускаем обработку
            result = service.process_new_group()
            
            assert result is True
            mock_retrain.assert_called_once()
            print("✅ Полный цикл обработки работает")
    
    def test_api_error_handling(self, mock_paths):
        """Тест обработки ошибок API"""
        print("🧪 Тест обработки ошибок API...")
        
        service = AutoLearningService()
        
        # Мокаем падающий API
        with patch('api_data.auto_learning_service.get_data_with_curl') as mock_api:
            mock_api.return_value = None
            
            # Запускаем обработку с ошибкой
            result = service.process_new_group()
            
            assert result is False
            assert service.consecutive_api_errors > 0
            print("✅ Обработка ошибок API работает")

if __name__ == "__main__":
    # Запуск тестов вручную
    pytest.main([__file__, '-v'])