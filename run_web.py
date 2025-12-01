# [file name]: run_web.py
#!/usr/bin/env python3
"""
Скрипт запуска веб-интерфейса
"""

import os
import sys

# Добавляем корневую директорию проекта в путь
project_root = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, project_root)

if __name__ == "__main__":
    # Запускаем веб-интерфейс
    os.system(f"streamlit run {os.path.join(project_root, 'web', 'app.py')}")
