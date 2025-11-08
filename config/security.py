# [file name]: config/security.py
"""
Безопасные операции с файлами и защита сервисов - ПОЛНАЯ ВЕРСИЯ
"""

import os
import json
import fcntl
import hashlib
import time
from pathlib import Path
from typing import Any, Callable, Dict
from config import logging_config

logger = logging_config.get_ml_system_logger()

class FileLock:
    """Блокировка файлов для предотвращения конфликтов"""
    
    def __init__(self, filename):
        # Преобразуем в Path если это строка
        self.filename = Path(filename) if isinstance(filename, str) else filename
        self.lockfile = self.filename.with_suffix(self.filename.suffix + '.lock')
        self.lockfile_fd = None
    
    def __enter__(self):
        """Вход в контекст блокировки"""
        try:
            # Создаем директорию если не существует
            self.lockfile.parent.mkdir(parents=True, exist_ok=True)
            
            # Открываем файл блокировки
            self.lockfile_fd = open(self.lockfile, 'w')
            
            # Пытаемся получить эксклюзивную блокировку
            fcntl.flock(self.lockfile_fd.fileno(), fcntl.LOCK_EX)
            
            return self
            
        except Exception as e:
            logger.warning(f"⚠️  Ошибка блокировки файла {self.filename}: {e}")
            # В случае ошибки все равно продолжаем
            return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Выход из контекста блокировки"""
        try:
            if self.lockfile_fd:
                # Снимаем блокировку и закрываем файл
                fcntl.flock(self.lockfile_fd.fileno(), fcntl.LOCK_UN)
                self.lockfile_fd.close()
                
                # Удаляем файл блокировки
                if self.lockfile.exists():
                    self.lockfile.unlink()
                    
        except Exception as e:
            logger.warning(f"⚠️  Ошибка разблокировки файла {self.filename}: {e}")

class SafeFileOperations:
    """Безопасные операции с JSON файлами"""
    
    @staticmethod
    def safe_json_operation(operation: Callable, filename, *args, **kwargs) -> Any:
        """Безопасное выполнение операции с JSON файлом"""
        # Преобразуем в Path если это строка
        file_path = Path(filename) if isinstance(filename, str) else filename
        
        with FileLock(file_path):
            return operation(file_path, *args, **kwargs)
    
    @staticmethod
    def read_json_safe(filename, default=None):
        """Безопасное чтение JSON файла"""
        def read_operation(file_path):
            if not file_path.exists():
                return default if default is not None else {}
            
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except (json.JSONDecodeError, Exception) as e:
                logger.error(f"❌ Ошибка чтения JSON файла {file_path}: {e}")
                return default if default is not None else {}
        
        return SafeFileOperations.safe_json_operation(read_operation, filename)
    
    @staticmethod
    def write_json_safe(filename, data):
        """Безопасная запись в JSON файл"""
        def write_operation(file_path):
            try:
                # Создаем директорию если не существует
                file_path.parent.mkdir(parents=True, exist_ok=True)
                
                with open(file_path, 'w', encoding='utf-8') as f:
                    json.dump(data, f, ensure_ascii=False, indent=2)
                
                logger.debug(f"💾 Файл сохранен: {file_path}")
                return True
                
            except Exception as e:
                logger.error(f"❌ Ошибка записи JSON файла {file_path}: {e}")
                return False
        
        return SafeFileOperations.safe_json_operation(write_operation, filename)

class DataValidator:
    """Валидация данных"""
    
    @staticmethod
    def validate_group(group_str: str) -> bool:
        """Валидация группы чисел"""
        try:
            numbers = [int(x) for x in group_str.strip().split()]
            if len(numbers) != 4:
                return False
            if not all(1 <= x <= 26 for x in numbers):
                return False
            if numbers[0] == numbers[1] or numbers[2] == numbers[3]:
                return False
            return True
        except:
            return False

class ServiceProtection:
    """Защита сервисов от сбоев и ошибок"""
    
    def __init__(self, max_errors: int = 3, reset_timeout: int = 3600):
        self.max_errors = max_errors
        self.reset_timeout = reset_timeout
        self.error_count = 0
        self.last_error_time = None
        self.service_active = True
    
    def check_service_health(self) -> bool:
        """Проверка здоровья сервиса"""
        if not self.service_active:
            return False
        
        # Сбрасываем счетчик ошибок если прошло достаточно времени
        if (self.last_error_time and 
            time.time() - self.last_error_time > self.reset_timeout):
            self.error_count = 0
            self.last_error_time = None
        
        return self.error_count < self.max_errors
    
    def record_error(self, error_message: str = None):
        """Запись ошибки сервиса"""
        self.error_count += 1
        self.last_error_time = time.time()
        
        if error_message:
            logger.error(f"❌ Ошибка сервиса #{self.error_count}: {error_message}")
        
        if self.error_count >= self.max_errors:
            self.service_active = False
            logger.critical(f"🚨 Сервис остановлен после {self.error_count} ошибок")
    
    def reset_errors(self):
        """Сброс счетчика ошибок"""
        self.error_count = 0
        self.last_error_time = None
        self.service_active = True
        logger.info("✅ Счетчик ошибок сервиса сброшен")
    
    def get_protection_status(self) -> Dict:
        """Получение статуса защиты"""
        return {
            'service_active': self.service_active,
            'error_count': self.error_count,
            'max_errors': self.max_errors,
            'last_error_time': self.last_error_time,
            'can_operate': self.check_service_health()
        }

class SecurityManager:
    """Менеджер безопасности системы"""
    
    def __init__(self):
        self.service_protection = ServiceProtection()
        self.data_validator = DataValidator()
    
    def validate_api_request(self, request_data: Dict) -> bool:
        """Валидация API запроса"""
        try:
            # Проверяем обязательные поля
            required_fields = ['action', 'timestamp']
            for field in required_fields:
                if field not in request_data:
                    return False
            
            # Проверяем timestamp (не старше 5 минут)
            current_time = time.time()
            request_time = request_data.get('timestamp', 0)
            if current_time - request_time > 300:  # 5 минут
                return False
            
            return True
            
        except Exception as e:
            logger.error(f"❌ Ошибка валидации API запроса: {e}")
            return False
    
    def create_request_signature(self, data: Dict, secret_key: str) -> str:
        """Создание подписи запроса"""
        try:
            # Сортируем данные для консистентности
            sorted_data = json.dumps(data, sort_keys=True, separators=(',', ':'))
            # Создаем подпись
            signature = hashlib.sha256(
                f"{sorted_data}{secret_key}".encode()
            ).hexdigest()
            return signature
        except Exception as e:
            logger.error(f"❌ Ошибка создания подписи: {e}")
            return ""
