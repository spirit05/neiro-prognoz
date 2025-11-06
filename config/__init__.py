"""
Пакет конфигурации модульной архитектуры
"""

from config.paths import (
    PROJECT_ROOT, ML_SYSTEM_DIR, SERVICES_DIR, WEB_DIR, CONFIG_DIR, DATA_DIR,
    DATASETS_DIR, MODELS_DIR, ANALYTICS_DIR, LOGS_DIR,
    DATASET_FILE, MODEL_FILE, PREDICTIONS_STATE_FILE, LEARNING_RESULTS_FILE,
    SERVICE_STATE_FILE, TELEGRAM_CONFIG_FILE, INFO_FILE,
    create_directories, migrate_old_data
)

from config.constants import (
    MAX_API_RETRIES, API_RETRY_DELAY, MAX_CONSECUTIVE_ERRORS,
    BUFFER_MINUTES, CRITICAL_INTERVAL_MINUTES, SCHEDULE_MINUTES,
    DEFAULT_EPOCHS, RETRAIN_EPOCHS, MIN_DATASET_SIZE, PREDICTION_TOP_K,
    HIGH_CONFIDENCE_THRESHOLD, MEDIUM_CONFIDENCE_THRESHOLD, LOW_CONFIDENCE_THRESHOLD,
    DEFAULT_TELEGRAM_CONFIG, DEFAULT_SERVICE_STATE, LEARNING_RESULTS_STRUCTURE
)

from config.logging_config import (
    setup_logging, get_ml_system_logger, get_auto_learning_logger,
    get_telegram_bot_logger, get_web_interface_logger, ProgressLogger
)

from config.security import (
    FileLock, SafeFileOperations, ServiceProtection, DataValidator
)

# Автоматическая миграция при первом импорте
try:
    migrate_old_data()
except Exception as e:
    print(f"⚠️ Предупреждение при миграции данных: {e}")

__all__ = [
    # Пути
    'PROJECT_ROOT', 'ML_SYSTEM_DIR', 'SERVICES_DIR', 'WEB_DIR', 'CONFIG_DIR', 'DATA_DIR',
    'DATASETS_DIR', 'MODELS_DIR', 'ANALYTICS_DIR', 'LOGS_DIR',
    'DATASET_FILE', 'MODEL_FILE', 'PREDICTIONS_STATE_FILE', 'LEARNING_RESULTS_FILE',
    'SERVICE_STATE_FILE', 'TELEGRAM_CONFIG_FILE', 'INFO_FILE',
    'create_directories', 'migrate_old_data',
    
    # Константы
    'MAX_API_RETRIES', 'API_RETRY_DELAY', 'MAX_CONSECUTIVE_ERRORS',
    'BUFFER_MINUTES', 'CRITICAL_INTERVAL_MINUTES', 'SCHEDULE_MINUTES',
    'DEFAULT_EPOCHS', 'RETRAIN_EPOCHS', 'MIN_DATASET_SIZE', 'PREDICTION_TOP_K',
    'HIGH_CONFIDENCE_THRESHOLD', 'MEDIUM_CONFIDENCE_THRESHOLD', 'LOW_CONFIDENCE_THRESHOLD',
    'DEFAULT_TELEGRAM_CONFIG', 'DEFAULT_SERVICE_STATE', 'LEARNING_RESULTS_STRUCTURE',
    
    # Логирование
    'setup_logging', 'get_ml_system_logger', 'get_auto_learning_logger',
    'get_telegram_bot_logger', 'get_web_interface_logger', 'ProgressLogger',
    
    # Безопасность
    'FileLock', 'SafeFileOperations', 'ServiceProtection', 'DataValidator'
]