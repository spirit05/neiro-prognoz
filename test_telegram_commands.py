#!/usr/bin/env python3
"""
Тест команд Telegram бота
"""

from services.telegram.commands import CommandHandler
from services.auto_learning.service import AutoLearningService

print("=== ТЕСТ КОМАНД TELEGRAM БОТА ===")

try:
    # Создаем сервис для тестирования
    auto_service = AutoLearningService()
    command_handler = CommandHandler(auto_service)
    
    # Тестируем команды
    test_commands = ['/start', '/help', '/status', '/service_status', '/predictions']
    
    for cmd in test_commands:
        print(f"\n🔧 Тестируем команду: {cmd}")
        response = command_handler.handle_command(cmd, 12345)
        print(f"   Ответ: {response[:100]}...")
    
    print("\n✅ Все команды протестированы!")
        
except Exception as e:
    print(f"❌ Ошибка тестирования команд: {e}")
    import traceback
    traceback.print_exc()
