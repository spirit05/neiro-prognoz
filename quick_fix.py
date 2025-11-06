# quick_fix.py
#!/usr/bin/env python3
"""
Быстрое исправление web/app.py
"""

import os

PROJECT_ROOT = '/home/spirit/Desktop/project'
web_app_path = os.path.join(PROJECT_ROOT, 'web', 'app.py')

# Читаем текущий файл
with open(web_app_path, 'r', encoding='utf-8') as f:
    content = f.read()

# Заменяем проблемную строку
old_line = 'from config.paths import DATASET, MODEL'
new_line = 'from config.paths import paths\nDATASET = paths.DATASET\nMODEL = paths.MODEL'

if old_line in content:
    content = content.replace(old_line, new_line)
    with open(web_app_path, 'w', encoding='utf-8') as f:
        f.write(content)
    print("✅ web/app.py исправлен")
else:
    print("✅ web/app.py уже исправлен")

print("\nТестируем исправление...")
os.system('python3 test_minimal.py')