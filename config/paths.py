import os

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

paths = Paths()

# Обратная совместимость для старых импортов
DATASET = paths.DATASET
MODEL = paths.MODEL
PREDICTIONS = paths.PREDICTIONS
LEARNING_RESULTS = paths.LEARNING_RESULTS
TELEGRAM_CONFIG = paths.TELEGRAM_CONFIG
SERVICE_STATE = paths.SERVICE_STATE
INFO_JSON = paths.INFO_JSON
TRAINING_LOG = paths.TRAINING_LOG
AUTO_LEARNING_LOG = paths.AUTO_LEARNING_LOG
SERVICE_RUNNER_LOG = paths.SERVICE_RUNNER_LOG
TELEGRAM_BOT_LOG = paths.TELEGRAM_BOT_LOG
WEB_INTERFACE_LOG = paths.WEB_INTERFACE_LOG
ML_SYSTEM_LOG = paths.ML_SYSTEM_LOG
API_CLIENT_LOG = paths.API_CLIENT_LOG
# Обратная совместимость для старых импортов
DATASET = paths.DATASET
MODEL = paths.MODEL
PREDICTIONS = paths.PREDICTIONS
LEARNING_RESULTS = paths.LEARNING_RESULTS
TELEGRAM_CONFIG = paths.TELEGRAM_CONFIG
SERVICE_STATE = paths.SERVICE_STATE
INFO_JSON = paths.INFO_JSON
TRAINING_LOG = paths.TRAINING_LOG
AUTO_LEARNING_LOG = paths.AUTO_LEARNING_LOG
SERVICE_RUNNER_LOG = paths.SERVICE_RUNNER_LOG
TELEGRAM_BOT_LOG = paths.TELEGRAM_BOT_LOG
WEB_INTERFACE_LOG = paths.WEB_INTERFACE_LOG
ML_SYSTEM_LOG = paths.ML_SYSTEM_LOG
API_CLIENT_LOG = paths.API_CLIENT_LOG
