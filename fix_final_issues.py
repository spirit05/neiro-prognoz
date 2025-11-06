# fix_final_issues.py
#!/usr/bin/env python3
"""
Финальное исправление оставшихся проблем
"""

import os
import sys

PROJECT_ROOT = '/home/spirit/Desktop/project'
sys.path.insert(0, PROJECT_ROOT)

def create_missing_files():
    """Создаем отсутствующие файлы"""
    print("🔧 Создаем отсутствующие файлы...")
    
    # Создаем директорию utils если не существует
    utils_dir = os.path.join(PROJECT_ROOT, 'utils')
    os.makedirs(utils_dir, exist_ok=True)
    
    # Создаем файлы с правильным содержимым
    files_to_create = {
        'config/paths.py': '''import os

def find_project_root():
    current_dir = os.path.dirname(os.path.abspath(__file__))
    potential_root = os.path.dirname(current_dir)
    expected_dirs = ['web', 'ml', 'services', 'data']
    if all(os.path.exists(os.path.join(potential_root, d)) for d in expected_dirs):
        return potential_root
    cwd = os.getcwd()
    if all(os.path.exists(os.path.join(cwd, d)) for d in expected_dirs):
        return cwd
    return '/opt/project'

PROJECT_ROOT = find_project_root()

class Paths:
    def __init__(self):
        self.PROJECT_ROOT = PROJECT_ROOT

    @property
    def DATASET(self):
        return os.path.join(self.PROJECT_ROOT, 'data', 'datasets', 'dataset.json')

    @property
    def PREDICTIONS(self):
        return os.path.join(self.PROJECT_ROOT, 'data', 'analytics', 'predictions.json')

    @property
    def LEARNING_RESULTS(self):
        return os.path.join(self.PROJECT_ROOT, 'data', 'analytics', 'learning_results.json')

    @property
    def MODEL(self):
        return os.path.join(self.PROJECT_ROOT, 'data', 'models', 'simple_model.pth')

    @property
    def TELEGRAM_CONFIG(self):
        return os.path.join(self.PROJECT_ROOT, 'config', 'telegram.json')

    @property
    def SERVICE_STATE(self):
        return os.path.join(self.PROJECT_ROOT, 'data', 'analytics', 'service_state.json')

    @property
    def INFO_JSON(self):
        return os.path.join(self.PROJECT_ROOT, 'data', 'analytics', 'info.json')

    @property
    def TRAINING_LOG(self):
        return os.path.join(self.PROJECT_ROOT, 'data', 'logs', 'training.log')

    @property
    def AUTO_LEARNING_LOG(self):
        return os.path.join(self.PROJECT_ROOT, 'data', 'logs', 'auto_learning.log')

    @property
    def SERVICE_RUNNER_LOG(self):
        return os.path.join(self.PROJECT_ROOT, 'data', 'logs', 'service_runner.log')

    @property
    def TELEGRAM_BOT_LOG(self):
        return os.path.join(self.PROJECT_ROOT, 'data', 'logs', 'telegram_bot.log')

    @property
    def WEB_INTERFACE_LOG(self):
        return os.path.join(self.PROJECT_ROOT, 'data', 'logs', 'web_interface.log')

    @property
    def ML_SYSTEM_LOG(self):
        return os.path.join(self.PROJECT_ROOT, 'data', 'logs', 'ml_system.log')

    @property
    def API_CLIENT_LOG(self):
        return os.path.join(self.PROJECT_ROOT, 'data', 'logs', 'api_client.log')

paths = Paths()''',
        
        'utils/logging_system.py': '''import logging
import os
import sys
from config.paths import paths

class ProjectLogger:
    _loggers = {}

    @classmethod
    def get_logger(cls, name, log_file=None, level=logging.INFO):
        if name in cls._loggers:
            return cls._loggers[name]
        logger = logging.getLogger(name)
        logger.setLevel(level)
        formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s', datefmt='%Y-%m-%d %H:%M:%S')
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setFormatter(formatter)
        logger.addHandler(console_handler)
        if log_file:
            os.makedirs(os.path.dirname(log_file), exist_ok=True)
            file_handler = logging.FileHandler(log_file, encoding='utf-8')
            file_handler.setFormatter(formatter)
            logger.addHandler(file_handler)
        cls._loggers[name] = logger
        return logger

def get_training_logger():
    return ProjectLogger.get_logger('Training', paths.TRAINING_LOG, logging.INFO)

def get_auto_learning_logger():
    return ProjectLogger.get_logger('Autolearning', paths.AUTO_LEARNING_LOG, logging.INFO)

def get_web_logger():
    return ProjectLogger.get_logger('WebInterface', paths.WEB_INTERFACE_LOG, logging.INFO)

def get_ml_system_logger():
    return ProjectLogger.get_logger('MLSystem', paths.ML_SYSTEM_LOG, logging.INFO)

def get_telegram_logger():
    return ProjectLogger.get_logger('TelegramBot', paths.TELEGRAM_BOT_LOG, logging.INFO)

def get_api_client_logger():
    return ProjectLogger.get_logger('APIClient', paths.API_CLIENT_LOG, logging.INFO)

def setup_all_loggers():
    loggers = [
        get_training_logger(),
        get_auto_learning_logger(),
        get_web_logger(),
        get_ml_system_logger(),
        get_telegram_logger(),
        get_api_client_logger(),
    ]
    for logger in loggers:
        logger.info(f"Логгер {logger.name} инициализирован")
    return loggers''',
        
        'utils/__init__.py': '''from .logging_system import (
    ProjectLogger,
    get_training_logger,
    get_auto_learning_logger,
    get_web_logger,
    get_ml_system_logger,
    get_telegram_logger,
    get_api_client_logger,
    setup_all_loggers
)'''
    }
    
    for file_path, content in files_to_create.items():
        full_path = os.path.join(PROJECT_ROOT, file_path)
        os.makedirs(os.path.dirname(full_path), exist_ok=True)
        with open(full_path, 'w', encoding='utf-8') as f:
            f.write(content)
        print(f"✅ Создан: {file_path}")

def test_system():
    """Тестируем систему после исправлений"""
    print("\n🔍 Тестируем систему...")
    
    try:
        from config.paths import paths
        print("✅ config.paths работает")
        
        from utils.logging_system import setup_all_loggers
        loggers = setup_all_loggers()
        print("✅ utils.logging_system работает")
        
        from web.app import main
        print("✅ web.app импортируется")
        
        print("\n🎉 ВСЕ СИСТЕМЫ РАБОТАЮТ!")
        return True
        
    except Exception as e:
        print(f"❌ Ошибка: {e}")
        import traceback
        traceback.print_exc()
        return False

def create_log_directories():
    """Создаем директории для логов"""
    print("\n📁 Создаем директории для логов...")
    
    log_dirs = [
        'data/logs',
        'data/datasets', 
        'data/models',
        'data/analytics'
    ]
    
    for dir_path in log_dirs:
        full_path = os.path.join(PROJECT_ROOT, dir_path)
        os.makedirs(full_path, exist_ok=True)
        print(f"✅ Создана: {dir_path}")

if __name__ == "__main__":
    print("🛠️ ФИНАЛЬНОЕ ИСПРАВЛЕНИЕ СИСТЕМЫ")
    print("=" * 50)
    
    create_missing_files()
    create_log_directories()
    success = test_system()
    
    print("\n" + "=" * 50)
    if success:
        print("🎉 СИСТЕМА ГОТОВА К ЗАПУСКУ!")
        print("\nЗапускайте веб-интерфейс:")
        print("streamlit run web/app.py")
    else:
        print("❌ Требуется дополнительная отладка")