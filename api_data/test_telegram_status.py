#!/usr/bin/env python3
"""
Тест команды /status в Telegram
"""

import os
import sys
import json
from datetime import datetime

# Добавляем пути
PROJECT_PATH = '/opt/project'
sys.path.insert(0, PROJECT_PATH)
sys.path.insert(0, os.path.dirname(__file__))

from auto_learning_service import AutoLearningService, TelegramNotifier

def test_telegram_status():
    """Тестируем отправку статуса в Telegram"""
    print("🧪 Тестируем команду /status в Telegram...")
    
    try:
        # Инициализируем сервис
        service = AutoLearningService()
        notifier = TelegramNotifier()
        
        # Получаем статус системы
        status_data = service.get_service_status()
        print("✅ Статус системы получен")
        
        # Форматируем сообщение статуса
        status_message = notifier.format_status_message(status_data)
        print("📋 Сообщение статуса сформировано:")
        print("=" * 50)
        print(status_message)
        print("=" * 50)
        
        # Отправляем в Telegram
        print("📤 Отправляем статус в Telegram...")
        success = notifier.send_message(status_message)
        
        if success:
            print("✅ Статус успешно отправлен в Telegram!")
            print("📱 Проверь бота - должно прийти сообщение со статусом системы")
        else:
            print("❌ Не удалось отправить статус в Telegram")
            print("💡 Проверь настройки bot_token и chat_id в telegram_config.json")
            
        return success
        
    except Exception as e:
        print(f"❌ Ошибка тестирования Telegram статуса: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    test_telegram_status()
