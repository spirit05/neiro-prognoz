# /opt/dev/web/run_web.py
"""
Запуск веб-интерфейса для новой архитектуры
"""
import sys
import os

# Устанавливаем пути
PROJECT_PATH = '/opt/dev'
sys.path.insert(0, PROJECT_PATH)

print(f"🚀 Запуск веб-интерфейса новой архитектуры...")
print(f"📁 Рабочая директория: {PROJECT_PATH}")

# Проверяем импорты
try:
    from web.integration.core import get_integration_manager
    from config.paths import PROJECT_ROOT
    
    print(f"✅ Импорты успешны")
    print(f"🌍 Среда: {'DEV' if 'dev' in str(PROJECT_ROOT).lower() else 'PROD'}")
    
    # Тестируем интеграцию
    manager = get_integration_manager()
    status = manager.get_system_status()
    print(f"✅ Система инициализирована: {status}")
    
except Exception as e:
    print(f"❌ Ошибка импорта: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

# Запускаем Streamlit
if __name__ == "__main__":
    # Импортируем и запускаем app.py через Streamlit
    from streamlit.web.cli import main
    
    sys.argv = [
        "streamlit", "run", 
        "web/app.py", 
        "--server.port=8501", 
        "--server.address=0.0.0.0",
        "--theme.base=light",
        "--browser.gatherUsageStats=false"
    ]
    
    print(f"🌐 Запуск Streamlit на порту 8501...")
    sys.exit(main())