#!/usr/bin/env python3
"""
Тест основного бота
"""

from services.telegram.bot import TelegramPollingBot

print("=== ТЕСТ ОСНОВНОГО TELEGRAM БОТА ===")

try:
    bot = TelegramPollingBot()
    bot_info = bot.get_bot_info()
    
    print("🤖 Информация о боте:")
    for key, value in bot_info.items():
        print(f"  {key}: {value}")
    
    print(f"\n📊 Статус готовности:")
    print(f"  Бот включен: {'✅ ДА' if bot_info['enabled'] else '❌ НЕТ'}")
    print(f"  Конфиг валиден: {'✅ ДА' if bot_info['config_valid'] else '❌ НЕТ'}")
    print(f"  Bot token установлен: {'✅ ДА' if bot_info['bot_token_set'] else '❌ НЕТ'}")
    print(f"  Chat ID установлен: {'✅ ДА' if bot_info['chat_id_set'] else '❌ НЕТ'}")
    print(f"  Автосервис доступен: {'✅ ДА' if bot_info['auto_service_available'] else '❌ НЕТ'}")
    
    if all([bot_info['enabled'], bot_info['config_valid'], bot_info['bot_token_set'], bot_info['chat_id_set']]):
        print("\n🎉 Бот полностью готов к работе!")
    else:
        print("\n⚠️ Бот требует настройки!")
        
except Exception as e:
    print(f"❌ Ошибка тестирования бота: {e}")
    import traceback
    traceback.print_exc()
