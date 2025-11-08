# /opt/dev/utils/find_streamlit_logs.py
#!/usr/bin/env python3
"""
Поиск логов Streamlit
"""

import os
import glob
from pathlib import Path

def find_streamlit_logs():
    """Поиск всех возможных мест с логами Streamlit"""
    possible_paths = [
        # 1. Логи в домашней директории пользователя
        Path.home() / '.streamlit' / 'logs',
        Path.home() / '.streamlit' / 'log.txt',
        
        # 2. Системные логи
        Path('/var/log/streamlit'),
        Path('/tmp/streamlit'),
        
        # 3. Логи в директории проекта
        Path('/opt/dev') / 'streamlit.log',
        Path('/opt/dev') / 'logs' / 'streamlit.log',
        Path('/opt/dev') / 'web' / 'streamlit.log',
        
        # 4. Стандартные системные логи
        Path('/var/log/syslog'),
        Path('/var/log/messages'),
        
        # 5. Логи в временных директориях
        Path('/tmp') / 'streamlit.log',
    ]
    
    print("🔍 Поиск логов Streamlit...")
    
    found_logs = []
    for path in possible_paths:
        if path.exists():
            if path.is_dir():
                # Ищем все .log файлы в директории
                log_files = list(path.glob('*.log'))
                found_logs.extend(log_files)
                print(f"📁 Директория: {path}")
                for log_file in log_files:
                    print(f"   📄 {log_file}")
            else:
                found_logs.append(path)
                print(f"📄 Файл: {path}")
    
    # Также ищем процессы Streamlit
    print("\n🔍 Поиск процессов Streamlit...")
    try:
        import subprocess
        result = subprocess.run(['pgrep', '-f', 'streamlit'], capture_output=True, text=True)
        if result.returncode == 0:
            pids = result.stdout.strip().split('\n')
            for pid in pids:
                if pid:
                    print(f"🎯 Процесс Streamlit: PID {pid}")
                    # Пробуем найти файлы которые открыл процесс
                    try:
                        lsof_result = subprocess.run(['lsof', '-p', pid], capture_output=True, text=True)
                        for line in lsof_result.stdout.split('\n'):
                            if '.log' in line or 'streamlit' in line.lower():
                                print(f"   📁 {line}")
                    except:
                        pass
    except Exception as e:
        print(f"⚠️ Ошибка поиска процессов: {e}")
    
    return found_logs

if __name__ == "__main__":
    logs = find_streamlit_logs()
    if not logs:
        print("❌ Логи Streamlit не найдены")
