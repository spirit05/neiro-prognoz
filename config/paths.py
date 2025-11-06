# config/paths.py
import os

# Динамическое определение корня проекта
def find_project_root():
    """Находит корень проекта автоматически"""
    # Текущая директория этого файла
    current_dir = os.path.dirname(os.path.abspath(__file__))

    # Поднимаемся на уровень выше (из config/ в корень)
    potential_root = os.path.dirname(current_dir)

    # Проверяем наличие ожидаемой структуры
    expected_dirs = ['web', 'ml', 'services', 'data']
    if all(os.path.exists(os.path.join(potential_root, dir)) for dir in expected_dirs):
        return potential_root

    # Если не нашли, используем текущую рабочую директорию
    cwd = os.getcwd()
    if all(os.path.exists(os.path.join(cwd, dir)) for dir in expected_dirs):
        return cwd

    # Запасной вариант для сервера
    return '/opt/project'

PROJECT_ROOT = find_project_root()

class Paths:
    """Единый менеджер путей для всего проекта"""

    def __init__(self):
        self.PROJECT_ROOT = PROJECT_ROOT

    # === ДАННЫЕ ===
    @property
    def DATASET(self):
        return os.path.join(self.PROJECT_ROOT, 'data', 'datasets', 'dataset.json')

    @property
    def PREDICTIONS(self):
        return os.path.join(self.PROJECT_ROOT, 'data', 'analytics', 'predictions_state.json')

    @property
    def LEARNING_RESULTS(self):
        return os.path.join(self.PROJECT_ROOT, 'data', 'analytics', 'learning_results.json')

    @property
    def MODEL(self):
        return os.path.join(self.PROJECT_ROOT, 'data', 'models', 'simple_model.pth')

    # === КОНФИГИ ===
    @property
    def TELEGRAM_CONFIG(self):
        return os.path.join(self.PROJECT_ROOT, 'config', 'telegram.json')

    @property
    def SERVICE_STATE(self):
        return os.path.join(self.PROJECT_ROOT, 'data', 'analytics', 'service_state.json')

    @property
    def INFO_JSON(self):
        return os.path.join(self.PROJECT_ROOT, 'data', 'analytics', 'info.json')

    # === ЛОГИ ===
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

    # === ДИРЕКТОРИИ ===
    @property
    def DATA_DIR(self):
        return os.path.join(self.PROJECT_ROOT, 'data')

    @property
    def DATASETS_DIR(self):
        return os.path.join(self.PROJECT_ROOT, 'data', 'datasets')

    @property
    def MODELS_DIR(self):
        return os.path.join(self.PROJECT_ROOT, 'data', 'models')

    @property
    def ANALYTICS_DIR(self):
        return os.path.join(self.PROJECT_ROOT, 'data', 'analytics')

    @property
    def LOGS_DIR(self):
        return os.path.join(self.PROJECT_ROOT, 'data', 'logs')

# Глобальный экземпляр для импорта
paths = Paths()