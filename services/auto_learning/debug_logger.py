# /opt/dev/services/auto_learning/debug_logger.py
import logging
from datetime import datetime
from pathlib import Path

class DebugLogger:
    def __init__(self):
        self.logger = logging.getLogger('auto_learning_debug')
        self.logger.setLevel(logging.DEBUG)
        
        # Создаем отдельный файл для дебага
        debug_file = Path('/opt/dev/data/logs/auto_learning_debug.log')
        debug_file.parent.mkdir(exist_ok=True)
        
        handler = logging.FileHandler(debug_file)
        formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
        handler.setFormatter(formatter)
        self.logger.addHandler(handler)
    
    def log_api_call(self, url, params, response):
        self.logger.debug(f"API Call: {url}")
        self.logger.debug(f"Params: {params}")
        self.logger.debug(f"Response status: {getattr(response, 'status_code', 'No status')}")
        self.logger.debug(f"Response content: {getattr(response, 'text', 'No content')}")
    
    def log_retraining_step(self, data_size, epochs, results):
        self.logger.debug(f"Retraining: {data_size} samples, {epochs} epochs")
        self.logger.debug(f"Training results: {results}")
    
    def log_system_state(self, service_state):
        self.logger.debug(f"System state: {service_state}")

