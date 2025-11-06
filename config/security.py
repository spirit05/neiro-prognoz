"""
Настройки безопасности и защитные механизмы
"""

import fcntl
import os
from pathlib import Path
from typing import Any, Callable
import json

class FileLock:
    """Класс для безопасных файловых операций с блокировкой"""
    
    def __init__(self, filename: Path):
        self.filename = filename
        self.lockfile = filename.with_suffix(filename.suffix + '.lock')
        self.fd = None
    
    def __enter__(self):
        """Вход в контекст блокировки"""
        self.fd = open(self.lockfile, 'w')
        try:
            fcntl.flock(self.fd.fileno(), fcntl.LOCK_EX | fcntl.LOCK_NB)
            return self
        except IOError:
            self.fd.close()
            raise RuntimeError(f"Файл {self.filename} заблокирован другим процессом")
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Выход из контекста блокировки"""
        if self.fd:
            fcntl.flock(self.fd.fileno(), fcntl.LOCK_UN)
            self.fd.close()
            try:
                os.remove(self.lockfile)
            except:
                pass

class SafeFileOperations:
    """Класс для безопасных файловых операций"""
    
    @staticmethod
    def safe_json_operation(operation: Callable, filename: Path, *args, **kwargs) -> Any:
        """
        Безопасная операция с JSON файлом
        
        Args:
            operation: Функция операции (read, write, update)
            filename: Путь к файлу
            *args, **kwargs: Аргументы операции
        
        Returns:
            Результат операции
        """
        from config.constants import MAX_API_RETRIES, API_RETRY_DELAY
        from config.logging_config import get_auto_learning_logger
        
        logger = get_auto_learning_logger()
        
        for attempt in range(MAX_API_RETRIES):
            try:
                with FileLock(filename):
                    return operation(filename, *args, **kwargs)
            except RuntimeError as e:
                if attempt < MAX_API_RETRIES - 1:
                    logger.warning(f"⚠️ Файл {filename} заблокирован. Попытка {attempt + 1}/{MAX_API_RETRIES}")
                    import time
                    time.sleep(API_RETRY_DELAY)
                else:
                    logger.error(f"❌ Не удалось получить доступ к файлу {filename}: {e}")
                    raise
    
    @staticmethod
    def read_json_safe(filename: Path, default: Any = None) -> Any:
        """Безопасное чтение JSON файла"""
        def read_operation(file_path):
            if not file_path.exists():
                return default
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except Exception as e:
                logger = get_auto_learning_logger()
                logger.error(f"❌ Ошибка чтения {file_path}: {e}")
                return default
        
        return SafeFileOperations.safe_json_operation(read_operation, filename)
    
    @staticmethod
    def write_json_safe(filename: Path, data: Any) -> bool:
        """Безопасная запись в JSON файл"""
        def write_operation(file_path, content):
            # Создаем директорию если не существует
            file_path.parent.mkdir(parents=True, exist_ok=True)
            
            with open(file_path, 'w', encoding='utf-8') as f:
                json.dump(content, f, ensure_ascii=False, indent=2)
            return True
        
        return SafeFileOperations.safe_json_operation(write_operation, filename, data)

# Защитные механизмы сервиса
class ServiceProtection:
    """Класс защитных механизмов сервиса"""
    
    @staticmethod
    def check_time_slot_buffer(minutes_until_slot: float) -> dict:
        """
        Проверка временного буфера и критического интервала
        
        Args:
            minutes_until_slot: Минут до временного слота
        
        Returns:
            dict: Результат проверки
        """
        from config.constants import BUFFER_MINUTES, CRITICAL_INTERVAL_MINUTES
        
        if minutes_until_slot <= CRITICAL_INTERVAL_MINUTES:
            return {
                'status': 'critical',
                'message': f'Критический интервал: {minutes_until_slot:.1f} минут до слота',
                'action': 'stop_service'
            }
        elif minutes_until_slot <= BUFFER_MINUTES:
            return {
                'status': 'buffer',
                'message': f'Используем буфер {BUFFER_MINUTES} минут (до слота: {minutes_until_slot:.1f} мин)',
                'action': 'use_buffer',
                'buffer_minutes': BUFFER_MINUTES
            }
        else:
            return {
                'status': 'normal',
                'message': f'Нормальный интервал: {minutes_until_slot:.1f} минут до слота',
                'action': 'proceed'
            }
    
    @staticmethod
    def should_stop_service(consecutive_errors: int, max_errors: int) -> bool:
        """
        Проверка необходимости остановки сервиса
        
        Args:
            consecutive_errors: Количество последовательных ошибок
            max_errors: Максимальное допустимое количество ошибок
        
        Returns:
            bool: True если сервис нужно остановить
        """
        return consecutive_errors >= max_errors

# Валидация данных
class DataValidator:
    """Класс валидации данных"""
    
    @staticmethod
    def validate_group(group_str: str) -> bool:
        """
        Валидация формата группы чисел
        
        Args:
            group_str: Строка с группой чисел
        
        Returns:
            bool: True если группа валидна
        """
        from config.constants import GROUP_SIZE, MIN_NUMBER, MAX_NUMBER
        
        try:
            numbers = [int(x) for x in group_str.strip().split()]
            
            # Проверка количества чисел
            if len(numbers) != GROUP_SIZE:
                return False
            
            # Проверка диапазона чисел
            for num in numbers:
                if num < MIN_NUMBER or num > MAX_NUMBER:
                    return False
            
            return True
            
        except (ValueError, AttributeError):
            return False
    
    @staticmethod
    def validate_draw_sequence(current_draw: str, expected_next: str) -> bool:
        """
        Валидация последовательности тиражей
        
        Args:
            current_draw: Текущий тираж
            expected_next: Ожидаемый следующий тираж
        
        Returns:
            bool: True если последовательность корректна
        """
        try:
            current = int(current_draw)
            expected = int(expected_next)
            return expected == current + 1
        except (ValueError, TypeError):
            return False