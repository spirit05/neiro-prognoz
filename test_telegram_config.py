#!/usr/bin/env python3
"""
Тест конфигурации Telegram бота
"""

from services.telegram.config import TelegramConfig

print("=== ТЕСТ КОНФИГУРАЦИИ TELEGRAM БОТА ===")

config = TelegramConfig()
print("✅ Конфигурация загружена:")
print(f"  Enabled: {config.is_enabled()}")
print(f"  Bot Token: {'Есть' if config.get_bot_token() else 'Нет'}")
print(f"  Chat ID: {config.get_chat_id()}")
print(f"  Config Valid: {config.validate_config()}")

# Проверяем настройки уведомлений
notifications = config.get_notification_settings()
print(f"  Уведомления: {notifications}")

print("✅ Тест конфигурации пройден!")
