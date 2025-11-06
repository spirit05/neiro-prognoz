# config/constants.py
"""
Константы проекта
"""

# === API НАСТРОЙКИ ===
MAX_API_RETRIES = 3
API_RETRY_DELAY = 30  # секунды
MAX_CONSECUTIVE_ERRORS = 3

# === РАСПИСАНИЕ ===
SCHEDULE_MINUTES = [14, 29, 44, 59]
BUFFER_MINUTES = 7
CRITICAL_INTERVAL_MINUTES = 2

# === МОДЕЛЬ ===
HISTORY_SIZE = 25
DEFAULT_EPOCHS = 20
RETRAIN_EPOCHS = 5
BATCH_SIZE = 64

# === ВАЛИДАЦИЯ ===
MIN_DATASET_SIZE = 50
MIN_HISTORY_LENGTH = 20
MIN_TRAINING_EXAMPLES = 100

# === TELEGRAM ===
TELEGRAM_TIMEOUT = 10
TELEGRAM_MAX_ATTEMPTS = 3

# === ФАЙЛОВЫЕ ОПЕРАЦИИ ===
FILE_LOCK_TIMEOUT = 30
MAX_FILE_RETRIES = 3

class Status:
    """Статусы сервиса"""
    ACTIVE = "active"
    STOPPED = "stopped"
    ERROR = "error"
    TRAINING = "training"
    PREDICTING = "predicting"

class ServiceType:
    """Типы сервисов"""
    AUTO_LEARNING = "auto_learning"
    WEB = "web"
    TELEGRAM = "telegram"