"""
Константы проекта для модульной архитектуры
"""

from datetime import timedelta

# API и сетевые настройки
MAX_API_RETRIES = 3
API_RETRY_DELAY = 30  # секунды
API_TIMEOUT = 10

# Защитные механизмы
MAX_CONSECUTIVE_ERRORS = 3
BUFFER_MINUTES = 7  # 🔧 Буфер для временных слотов
CRITICAL_INTERVAL_MINUTES = 2  # 🔧 Критический интервал

# Расписание автообучения
SCHEDULE_MINUTES = [14, 29, 44, 59]  # 🔧 ФИКСИРОВАННОЕ РАСПИСАНИЕ

# === ДОБАВЛЕННЫЕ ПАРАМЕТРЫ ОБУЧЕНИЯ ===
# Основное обучение
MAIN_TRAINING_EPOCHS = 20
MAIN_BATCH_SIZE = 32
MAIN_LEARNING_RATE = 0.001

# Дообучение (автосервис)  
RETRAIN_EPOCHS = 3
RETRAIN_BATCH_SIZE = 16
RETRAIN_LEARNING_RATE = 0.0005

# Параметры ансамбля
ENSEMBLE_TOP_K = 4
ENSEMBLE_MIN_CONFIDENCE = 0.01

# Параметры самообучения
SELF_LEARNING_RETRAIN_EPOCHS = 2
SELF_LEARNING_ANALYSIS_WINDOW = 50
# === КОНЕЦ ДОБАВЛЕННЫХ ПАРАМЕТРОВ ===

# Настройки модели
DEFAULT_EPOCHS = 20
MIN_DATASET_SIZE = 50
PREDICTION_TOP_K = 4  # ✅ Только TOP-4 прогноза вместо 10

# Пороги уверенности
HIGH_CONFIDENCE_THRESHOLD = 0.02
MEDIUM_CONFIDENCE_THRESHOLD = 0.01
LOW_CONFIDENCE_THRESHOLD = 0.0005

# Форматы данных
GROUP_SIZE = 4
MIN_NUMBER = 1
MAX_NUMBER = 26

# URLs
API_GET_GROUP_URI = 'https://www.stoloto.ru/p/api/mobile/api/v35/service/games/details/draw-combination?game=dvazhdydva&draw='
API_GET_LAST_DRAW_URI = 'https://www.stoloto.ru/p/api/mobile/api/v35/service/games/details/time-to-draw'

# Telegram настройки по умолчанию
DEFAULT_TELEGRAM_CONFIG = {
    "enabled": True,
    "bot_token": "YOUR_BOT_TOKEN_HERE",
    "chat_id": "YOUR_CHAT_ID_HERE",
    "notifications": {
        "critical_errors": True,
        "all_errors": True,
        "service_stop": True,
        "predictions": False,
        "status_command": True
    }
}

# Состояние сервиса по умолчанию
DEFAULT_SERVICE_STATE = {
    "last_processed_draw": None,
    "service_active": False,
    "consecutive_api_errors": 0,
    "last_update": None
}

# Структура аналитики самообучения
LEARNING_RESULTS_STRUCTURE = {
    "predictions_accuracy": [],
    "model_performance": {},
    "learning_patterns": {},
    "last_analysis": None,
    "error_patterns": []
}
