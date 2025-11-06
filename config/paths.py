# config/paths.py
import os

# Простое определение корня проекта
def get_project_root():
    """Определяет корень проекта"""
    # Текущая директория этого файла
    current_dir = os.path.dirname(os.path.abspath(__file__))
    # Поднимаемся на уровень выше (из config/ в корень)
    return os.path.dirname(current_dir)

PROJECT_ROOT = get_project_root()

# Простые переменные путей
DATASET = os.path.join(PROJECT_ROOT, 'data', 'datasets', 'dataset.json')
PREDICTIONS = os.path.join(PROJECT_ROOT, 'data', 'analytics', 'predictions_state.json')
LEARNING_RESULTS = os.path.join(PROJECT_ROOT, 'data', 'analytics', 'learning_results.json')
MODEL = os.path.join(PROJECT_ROOT, 'data', 'models', 'simple_model.pth')
TELEGRAM_CONFIG = os.path.join(PROJECT_ROOT, 'config', 'telegram.json')
SERVICE_STATE = os.path.join(PROJECT_ROOT, 'data', 'analytics', 'service_state.json')
INFO_JSON = os.path.join(PROJECT_ROOT, 'data', 'analytics', 'info.json')
AUTO_LEARNING_LOG = os.path.join(PROJECT_ROOT, 'data', 'logs', 'auto_learning.log')
TRAINING_LOG = os.path.join(PROJECT_ROOT, 'data', 'logs', 'training.log')
SERVICE_RUNNER_LOG = os.path.join(PROJECT_ROOT, 'data', 'logs', 'service_runner.log')
DATA_DIR = os.path.join(PROJECT_ROOT, 'data')
DATASETS_DIR = os.path.join(PROJECT_ROOT, 'data', 'datasets')
MODELS_DIR = os.path.join(PROJECT_ROOT, 'data', 'models')
ANALYTICS_DIR = os.path.join(PROJECT_ROOT, 'data', 'analytics')
LOGS_DIR = os.path.join(PROJECT_ROOT, 'data', 'logs')