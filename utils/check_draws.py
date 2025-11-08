# /opt/dev/utils/check_draws.py
#!/usr/bin/env python3
"""
Утилита для проверки информации о тиражах
"""

import json
import logging
from pathlib import Path

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger('DrawChecker')

def check_draw_info():
    """Проверка информации о тиражах"""
    info_path = Path('/opt/dev/data/info.json')
    
    if not info_path.exists():
        logger.error("❌ Файл info.json не существует!")
        return
    
    try:
        with open(info_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        print("🎯 ИНФОРМАЦИЯ О ТИРАЖАХ:")
        print(f"📊 Текущий тираж: {data.get('current_draw', 'НЕТ ДАННЫХ')}")
        
        history = data.get('history', [])
        print(f"📋 Всего записей в истории: {len(history)}")
        
        if history:
            print("\n📜 ПОСЛЕДНИЕ 5 ТИРАЖЕЙ:")
            for entry in history[-5:]:
                processed = "✅" if entry.get('processed') else "❌"
                print(f"   {processed} Тираж {entry.get('draw')}: {entry.get('combination')} - {entry.get('timestamp', '')}")
        
        # Анализ тиражей
        if history:
            draws = [int(entry.get('draw', 0)) for entry in history if entry.get('draw')]
            if draws:
                print(f"\n🔢 МИНИМАЛЬНЫЙ ТИРАЖ: {min(draws)}")
                print(f"🔢 МАКСИМАЛЬНЫЙ ТИРАЖ: {max(draws)}")
                print(f"🔢 СЛЕДУЮЩИЙ ТИРАЖ: {max(draws) + 1}")
        
    except Exception as e:
        logger.error(f"❌ Ошибка чтения info.json: {e}")

if __name__ == "__main__":
    check_draw_info()

