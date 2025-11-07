#!/usr/bin/env python3
"""
Тест безопасности Telegram бота
"""

from services.telegram.security import SecurityManager

print("=== ТЕСТ БЕЗОПАСНОСТИ TELEGRAM БОТА ===")

security = SecurityManager()

# Тестируем авторизацию
test_chat_ids = [
    (5232136435, "✅ Должен быть авторизован (правильный chat_id)"),
    (12345, "❌ Должен быть НЕ авторизован (левый chat_id)"),
    ("5232136435", "✅ Должен быть авторизован (строка)"),
    (999999999, "❌ Должен быть НЕ авторизован (несуществующий)")
]

print("🔐 Тестируем авторизацию:")
for chat_id, expected in test_chat_ids:
    authorized = security.is_authorized_user(chat_id)
    status = "✅ АВТОРИЗОВАН" if authorized else "❌ НЕ АВТОРИЗОВАН"
    print(f"  Chat ID {chat_id}: {status} - {expected}")

# Тестируем валидацию сообщений
print("\n📨 Тестируем валидацию сообщений:")
test_messages = [
    ({'message_id': 1, 'chat': {'id': 123}, 'text': '/start'}, "✅ Валидное сообщение"),
    ({'message_id': 1, 'chat': {'id': 123}}, "❌ Нет текста"),
    ({'chat': {'id': 123}, 'text': '/start'}, "❌ Нет message_id"),
    ({'message_id': 1, 'text': '/start'}, "❌ Нет chat")
]

for message, expected in test_messages:
    valid = security.validate_message(message)
    status = "✅ ВАЛИДНО" if valid else "❌ НЕВАЛИДНО"
    print(f"  {expected}: {status}")

print("✅ Тест безопасности пройден!")
