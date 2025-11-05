#!/usr/bin/env python3
import sys
import os
sys.path.insert(0, '/opt/project')
sys.path.insert(0, '/opt/project/api_data')

try:
    from get_group import get_data_with_curl
    print("✅ Модуль get_group загружен успешно")
    
    result = get_data_with_curl()
    if result:
        print(f"✅ API запрос успешен: {result}")
    else:
        print("❌ API запрос вернул None")
        
except Exception as e:
    print(f"❌ Ошибка при импорте или вызове get_data_with_curl: {e}")
    import traceback
    traceback.print_exc()
