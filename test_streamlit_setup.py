# test_streamlit_setup.py
#!/usr/bin/env python3
"""
Быстрая проверка установки Streamlit и всех зависимостей
"""

import sys
import subprocess
import importlib

def test_imports():
    """Проверяем импорт всех необходимых библиотек"""
    print("🧪 Проверяем импорт библиотек...")
    
    libraries = [
        'streamlit',
        'torch',
        'numpy', 
        'scipy',
        'schedule',
        'requests',
        'json',
        'os',
        'sys'
    ]
    
    for lib in libraries:
        try:
            importlib.import_module(lib)
            print(f"✅ {lib}")
        except ImportError as e:
            print(f"❌ {lib}: {e}")
            return False
    
    return True

def test_project_imports():
    """Проверяем импорт наших модулей"""
    print("\n🔧 Проверяем импорт модулей проекта...")
    
    PROJECT_ROOT = '/home/spirit/Desktop/project'
    sys.path.insert(0, PROJECT_ROOT)
    
    modules = [
        'web.app',
        'ml.core.system',
        'services.auto_learning.service',
        'config.paths'
    ]
    
    for module in modules:
        try:
            importlib.import_module(module)
            print(f"✅ {module}")
        except Exception as e:
            print(f"❌ {module}: {e}")
            return False
    
    return True

def test_streamlit_command():
    """Проверяем что Streamlit доступен из командной строки"""
    print("\n🌐 Проверяем команду Streamlit...")
    
    try:
        result = subprocess.run(['streamlit', 'version'], 
                              capture_output=True, text=True)
        if result.returncode == 0:
            print(f"✅ Streamlit: {result.stdout.strip()}")
            return True
        else:
            print(f"❌ Streamlit: {result.stderr}")
            return False
    except Exception as e:
        print(f"❌ Streamlit command: {e}")
        return False

if __name__ == "__main__":
    print("🚀 Проверка установки Streamlit и зависимостей")
    print("=" * 50)
    
    success1 = test_imports()
    success2 = test_project_imports() 
    success3 = test_streamlit_command()
    
    print("\n" + "=" * 50)
    if success1 and success2 and success3:
        print("🎉 ВСЕ ПРОВЕРКИ ПРОЙДЕНЫ!")
        print("📋 Система готова к запуску!")
    else:
        print("💥 Есть проблемы с установкой!")
        sys.exit(1)