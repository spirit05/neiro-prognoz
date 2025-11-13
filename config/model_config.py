import yaml
from pydantic import BaseSettings
from pathlib import Path

class ModelConfig(BaseSettings):
    """Конфигурация модели"""
    
    model_name: str = "neiro-prognoz-v2"
    version: str = "1.0.0"
    
    @classmethod
    def from_yaml(cls, config_path: str = "config/model_config.yaml"):
        """Загрузка конфигурации из YAML"""
        path = Path(config_path)
        if not path.exists():
            raise FileNotFoundError(f"Config file not found: {config_path}")
            
        with open(path, 'r') as f:
            config_data = yaml.safe_load(f)
            
        return cls(**config_data)
