# [file name]: ml/data/providers/dataset_manager.py
"""
Менеджер dataset.json для новой архитектуры
"""

import json
import os
from typing import List, Optional
from pathlib import Path
import logging


class DatasetManager:
    """Управление dataset.json в новой архитектуре"""
    
    def __init__(self, dataset_path: Optional[str] = None):
        self.logger = logging.getLogger(__name__)
        
        if dataset_path:
            self.dataset_path = Path(dataset_path)
        else:
            # Путь по умолчанию в новой архитектуре
            self.dataset_path = Path("/opt/model/data/datasets/dataset.json")
        
        # Создаем директорию если не существует
        self.dataset_path.parent.mkdir(parents=True, exist_ok=True)
        
        self.logger.info(f"✅ DatasetManager инициализирован с путем: {self.dataset_path}")

    def load_dataset(self) -> List[str]:
        """Загрузка dataset.json"""
        if not self.dataset_path.exists():
            self.logger.warning(f"⚠️ Файл dataset.json не найден: {self.dataset_path}")
            return []
        
        try:
            with open(self.dataset_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            if not isinstance(data, list):
                self.logger.error("❌ dataset.json должен содержать список")
                return []
            
            self.logger.info(f"✅ Загружено {len(data)} групп из dataset.json")
            return data
            
        except Exception as e:
            self.logger.error(f"❌ Ошибка загрузки dataset.json: {e}")
            return []

    def save_dataset(self, data: List[str]) -> bool:
        """Сохранение dataset.json"""
        try:
            # Валидация данных перед сохранением
            valid_data = [group for group in data if self._validate_group_format(group)]
            
            with open(self.dataset_path, 'w', encoding='utf-8') as f:
                json.dump(valid_data, f, ensure_ascii=False, indent=2)
            
            self.logger.info(f"✅ Сохранено {len(valid_data)} групп в dataset.json")
            return True
            
        except Exception as e:
            self.logger.error(f"❌ Ошибка сохранения dataset.json: {e}")
            return False

    def add_groups(self, new_groups: List[str]) -> bool:
        """Добавление новых групп в dataset"""
        try:
            current_data = self.load_dataset()
            
            # Фильтруем дубликаты и невалидные группы
            valid_new_groups = []
            for group in new_groups:
                if (self._validate_group_format(group) and 
                    group not in current_data and 
                    group not in valid_new_groups):
                    valid_new_groups.append(group)
            
            if not valid_new_groups:
                self.logger.info("ℹ️ Нет новых валидных групп для добавления")
                return True
            
            # Добавляем новые группы
            updated_data = current_data + valid_new_groups
            
            # Сохраняем обновленный dataset
            success = self.save_dataset(updated_data)
            
            if success:
                self.logger.info(f"✅ Добавлено {len(valid_new_groups)} новых групп")
            else:
                self.logger.error("❌ Не удалось добавить новые группы")
            
            return success
            
        except Exception as e:
            self.logger.error(f"❌ Ошибка добавления групп: {e}")
            return False

    def get_dataset_stats(self) -> dict:
        """Статистика dataset"""
        data = self.load_dataset()
        
        # Анализ групп
        valid_groups = 0
        number_distribution = {}
        
        for group in data:
            if self._validate_group_format(group):
                valid_groups += 1
                numbers = [int(x) for x in group.strip().split()]
                for num in numbers:
                    number_distribution[num] = number_distribution.get(num, 0) + 1
        
        stats = {
            "total_groups": len(data),
            "valid_groups": valid_groups,
            "invalid_groups": len(data) - valid_groups,
            "number_distribution": number_distribution,
            "dataset_size_mb": self.dataset_path.stat().st_size / (1024 * 1024) if self.dataset_path.exists() else 0
        }
        
        return stats

    def _validate_group_format(self, group_str: str) -> bool:
        """Валидация формата группы"""
        try:
            if not isinstance(group_str, str):
                return False
            
            numbers = [int(x) for x in group_str.strip().split()]
            
            # Проверяем формат: 4 числа в диапазоне 1-26
            if len(numbers) != 4:
                return False
            
            if not all(1 <= x <= 26 for x in numbers):
                return False
            
            # Проверяем что пары не одинаковые
            if numbers[0] == numbers[1] or numbers[2] == numbers[3]:
                return False
            
            return True
            
        except:
            return False

    def backup_dataset(self, backup_suffix: str = "backup") -> bool:
        """Создание бэкапа dataset"""
        if not self.dataset_path.exists():
            self.logger.warning("⚠️ Нет dataset для бэкапа")
            return False
        
        try:
            backup_path = self.dataset_path.with_suffix(f".{backup_suffix}.json")
            import shutil
            shutil.copy2(self.dataset_path, backup_path)
            
            self.logger.info(f"✅ Создан бэкап: {backup_path}")
            return True
            
        except Exception as e:
            self.logger.error(f"❌ Ошибка создания бэкапа: {e}")
            return False
