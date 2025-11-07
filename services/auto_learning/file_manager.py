#!/usr/bin/env python3
"""
Менеджер файловых операций с блокировками
"""

import os
import fcntl
import json
from typing import Callable, Any

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

def safe_file_operation(operation: Callable, filename: str, *args, **kwargs) -> Any:
    """Безопасная операция с файлом с блокировкой"""
    max_retries = 3
    retry_delay = 30
    
    for attempt in range(max_retries):
        try:
            with FileLock(filename):
                return operation(filename, *args, **kwargs)
        except RuntimeError as e:
            if attempt < max_retries - 1:
                print(f"⚠️ Файл {filename} заблокирован. Попытка {attempt + 1}/{max_retries}")
                import time
                time.sleep(retry_delay)
            else:
                print(f"❌ Не удалось получить доступ к файлу {filename}: {e}")
                raise