# services/auto_learning/file_manager.py
"""
Управление файлами и блокировками
"""
import os
import json
import fcntl
from config.paths import DATA_DIR, DATASET, PREDICTIONS, LEARNING_RESULTS, INFO_JSON, SERVICE_STATE
from config.constants import MAX_FILE_RETRIES, FILE_LOCK_TIMEOUT

class FileLock:
    """Класс для блокировки файлов"""
    def __init__(self, filename):
        self.filename = filename
        self.lockfile = filename + ".lock"
        self.fd = None
    
    def __enter__(self):
        self.fd = open(self.lockfile, 'w')
        try:
            fcntl.flock(self.fd.fileno(), fcntl.LOCK_EX | fcntl.LOCK_NB)
            return self
        except IOError:
            self.fd.close()
            raise RuntimeError(f"Файл {self.filename} заблокирован другим процессом")
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        if self.fd:
            fcntl.flock(self.fd.fileno(), fcntl.LOCK_UN)
            self.fd.close()
            try:
                os.remove(self.lockfile)
            except:
                pass

def safe_file_operation(operation, filename, *args, **kwargs):
    """Безопасная операция с файлом с блокировкой"""
    for attempt in range(MAX_FILE_RETRIES):
        try:
            with FileLock(filename):
                return operation(filename, *args, **kwargs)
        except RuntimeError as e:
            if attempt < MAX_FILE_RETRIES - 1:
                import time
                time.sleep(FILE_LOCK_TIMEOUT)
            else:
                raise e

def ensure_data_dirs():
    """Создает необходимые директории данных"""
    directories = [DATA_DIR, os.path.dirname(DATASET), os.path.dirname(PREDICTIONS), 
                   os.path.dirname(LEARNING_RESULTS), os.path.dirname(INFO_JSON)]
    
    for directory in directories:
        os.makedirs(directory, exist_ok=True)

def load_json_safe(filename):
    """Безопасная загрузка JSON файла"""
    def read_operation(filename):
        if not os.path.exists(filename):
            return {}
        with open(filename, 'r', encoding='utf-8') as f:
            return json.load(f)
    
    return safe_file_operation(read_operation, filename)

def save_json_safe(data, filename):
    """Безопасное сохранение JSON файла"""
    def write_operation(filename):
        ensure_data_dirs()
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
    
    return safe_file_operation(write_operation, filename)