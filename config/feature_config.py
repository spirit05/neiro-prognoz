import yaml
from pydantic import BaseModel
from pathlib import Path

class FeatureConfig(BaseModel):
    """Конфигурация фич"""
    
    class Config:
        env_file = ".env"
    
    @classmethod
    def from_yaml(cls, config_path: str = "config/feature_config.yaml"):
        """Загрузка конфигурации из YAML"""
        path = Path(config_path)
        if not path.exists():
            raise FileNotFoundError(f"Config file not found: {config_path}")
            
        with open(path, 'r') as f:
            config_data = yaml.safe_load(f)
            
        return cls(**config_data)
