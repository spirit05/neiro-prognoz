# tests/integration/test_telegram_bot.py
"""
ТЕСТЫ TELEGRAM БОТА - уведомления и команды
"""
import pytest
from unittest.mock import patch, MagicMock

def test_telegram_status_command():
    """Тест команды /status в Telegram"""
    print("🧪 Тест Telegram команды /status...")
    
    with patch('api_data.auto_learning_service.requests') as mock_requests:
        from api_data.auto_learning_service import TelegramNotifier
        
        # Настраиваем моки
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            'ok': True,
            'result': [{
                'update_id': 123,
                'message': {'text': '/status', 'chat': {'id': 456}}
            }]
        }
        mock_requests.get.return_value = mock_response
        mock_requests.post.return_value = MagicMock(status_code=200)
        
        notifier = TelegramNotifier()
        notifier.config = {
            'enabled': True,
            'bot_token': 'TEST_TOKEN',
            'chat_id': 'TEST_CHAT',
            'notifications': {'status_command': True}
        }
        
        # Тестируем обработку статуса
        status_data = {
            'service_active': True,
            'model_trained': True,
            'dataset_size': 100
        }
        
        notifier.process_status_command(status_data)
        print("✅ Команда /status обработана")