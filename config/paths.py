"""
Единый менеджер путей для модульной архитектуры - DEV СРЕДА
"""

import os
from pathlib import Path

# 🔧 ОПРЕДЕЛЯЕМ СРЕДУ - DEV ИЛИ PROD
def get_project_root():
    """Определяем корневую директорию в зависимости от среды"""
    dev_path = Path("/opt/dev")
    prod_path = Path("/opt/project")
    
    # Проверяем, какая директория существует
    if dev_path.exists():
        print(f"🚀 Работаем в DEV среде: {dev_path}")
        return dev_path
    elif prod_path.exists():
        print(f"📦 Работаем в PROD среде: {prod_path}")
        return prod_path
    else:
        # Если ни одна не существует, создаем dev
        dev_path.mkdir(parents=True, exist_ok=True)
        print(f"🆕 Создана DEV среда: {dev_path}")
        return dev_path

# Базовые пути
PROJECT_ROOT = get_project_root()
OLD_PROJECT_ROOT = Path("/Desktop/project")  # Для обратной совместимости

# Основные директории
ML_SYSTEM_DIR = PROJECT_ROOT / "ml"
SERVICES_DIR = PROJECT_ROOT / "services" 
WEB_DIR = PROJECT_ROOT / "web"
CONFIG_DIR = PROJECT_ROOT / "config"
DATA_DIR = PROJECT_ROOT / "data"
TESTS_DIR = PROJECT_ROOT / "tests"

# Данные и модели
DATASETS_DIR = DATA_DIR / "datasets"
MODELS_DIR = DATA_DIR / "models"
ANALYTICS_DIR = DATA_DIR / "analytics"
LOGS_DIR = DATA_DIR / "logs"

# ML модули
ML_CORE_DIR = ML_SYSTEM_DIR / "core"
ML_ENSEMBLE_DIR = ML_SYSTEM_DIR / "ensemble"
ML_FEATURES_DIR = ML_SYSTEM_DIR / "features"
ML_LEARNING_DIR = ML_SYSTEM_DIR / "learning"
ML_UTILS_DIR = ML_SYSTEM_DIR / "utils"

# Сервисы
AUTO_LEARNING_DIR = SERVICES_DIR / "auto_learning"
TELEGRAM_DIR = SERVICES_DIR / "telegram"
MONITORING_DIR = SERVICES_DIR / "monitoring"

# Файлы данных
DATASET_FILE = DATASETS_DIR / "dataset.json"
MODEL_FILE = MODELS_DIR / "simple_model.pth"
PREDICTIONS_STATE_FILE = ANALYTICS_DIR / "predictions_state.json"
LEARNING_RESULTS_FILE = ANALYTICS_DIR / "learning_results.json"
SERVICE_STATE_FILE = ANALYTICS_DIR / "service_state.json"

# Конфигурационные файлы
TELEGRAM_CONFIG_FILE = SERVICES_DIR / "telegram" / "telegram_config.json"
INFO_FILE = ANALYTICS_DIR / "info.json"

# Логи
AUTO_LEARNING_LOG = LOGS_DIR / "auto_learning.log"
ML_SYSTEM_LOG = LOGS_DIR / "ml_system.log"
TELEGRAM_BOT_LOG = LOGS_DIR / "telegram_bot.log"

# Создание необходимых директорий
def create_directories():
    """Создание всех необходимых директорий в DEV среде"""
    directories = [
        ML_CORE_DIR, ML_ENSEMBLE_DIR, ML_FEATURES_DIR, ML_LEARNING_DIR, ML_UTILS_DIR,
        AUTO_LEARNING_DIR, TELEGRAM_DIR, MONITORING_DIR,
        DATASETS_DIR, MODELS_DIR, ANALYTICS_DIR, LOGS_DIR
    ]
    
    for directory in directories:
        directory.mkdir(parents=True, exist_ok=True)
        print(f"✅ Создана директория: {directory}")

# Пути для обратной совместимости (старая структура)
COMPATIBILITY_PATHS = {
    'old_model_path': OLD_PROJECT_ROOT / "data" / "models" / "simple_model.pth",
    'old_dataset_path': OLD_PROJECT_ROOT / "data" / "dataset.json",
    'old_service_state': OLD_PROJECT_ROOT / "api_data" / "service_state.json",
    'old_telegram_config': OLD_PROJECT_ROOT / "api_data" / "telegram_config.json"
}

def migrate_old_data():
    """Миграция данных из старой структуры в новую DEV среду"""
    print("🔄 Миграция данных из старой структуры в DEV...")
    
    migrations = [
        (COMPATIBILITY_PATHS['old_model_path'], MODEL_FILE),
        (COMPATIBILITY_PATHS['old_dataset_path'], DATASET_FILE),
        (COMPATIBILITY_PATHS['old_service_state'], SERVICE_STATE_FILE),
        (COMPATIBILITY_PATHS['old_telegram_config'], TELEGRAM_CONFIG_FILE)
    ]
    
    migrated_count = 0
    for old_path, new_path in migrations:
        if old_path.exists() and not new_path.exists():
            try:
                import shutil
                shutil.copy2(old_path, new_path)
                print(f"✅ Мигрирован: {old_path} -> {new_path}")
                migrated_count += 1
            except Exception as e:
                print(f"❌ Ошибка миграции {old_path}: {e}")
        elif new_path.exists():
            print(f"📁 Файл уже существует в DEV: {new_path}")
        else:
            print(f"📝 Исходный файл не найден: {old_path}")
    
    print(f"🎯 Мигрировано файлов: {migrated_count}/{len(migrations)}")

# Инициализация при импорте
create_directories()
migrate_old_data()