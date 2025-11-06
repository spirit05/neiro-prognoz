# run_web.py
#!/usr/bin/env python3
"""
Запуск веб-интерфейса - ОБНОВЛЕННЫЙ
"""

import os
import sys
import subprocess

# Добавляем корень проекта в путь
PROJECT_ROOT = '/home/spirit/Desktop/project'
sys.path.insert(0, PROJECT_ROOT)

def main():
    """Запуск веб-интерфейса"""
    print("🚀 Запуск веб-интерфейса AI Prediction System...")
    
    # Проверяем наличие необходимых файлов
    required_files = [
        os.path.join(PROJECT_ROOT, 'web', 'app.py'),
        os.path.join(PROJECT_ROOT, 'config', 'paths.py'),
        os.path.join(PROJECT_ROOT, 'ml', 'core', 'system.py')
    ]
    
    for file_path in required_files:
        if not os.path.exists(file_path):
            print(f"❌ Не найден файл: {file_path}")
            return False
    
    print("✅ Все необходимые файлы найдены")
    
    # Запускаем Streamlit
    try:
        cmd = [
            'streamlit', 'run', 
            os.path.join(PROJECT_ROOT, 'web', 'app.py'),
            '--server.port=8501',
            '--server.address=0.0.0.0'
        ]
        subprocess.run(cmd, check=True)
    except subprocess.CalledProcessError as e:
        print(f"❌ Ошибка запуска Streamlit: {e}")
        return False
    except KeyboardInterrupt:
        print("\n🛑 Веб-интерфейс остановлен")
    
    return True

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)