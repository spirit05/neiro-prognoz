# [file name]: ml/core/orchestrator/managers/data_manager.py
"""
DataManager - управление данными и их обработкой
"""

import numpy as np
import pandas as pd
from typing import List, Tuple, Dict, Optional, Any
import logging

from ml.core.types import DataBatch, DataType
from ml.data.processors.data_processor import SimpleDataBatch


class DataManager:
    """Менеджер данных - обработка, валидация, управление dataset"""

    def __init__(self, orchestrator):
        self.orchestrator = orchestrator
        self.logger = logging.getLogger(__name__)

        # Инициализация компонентов обработки данных
        self.orchestrator._init_data_processing_components()

        self.logger.info("✅ DataManager инициализирован")

    def prepare_training_data(self) -> Tuple[DataBatch, DataBatch]:
        """Подготовка данных для обучения через Data Processor"""
        if not self.orchestrator.data_processor:
            raise ValueError("Data Processor не инициализирован")

        if not self.orchestrator.dataset_manager:
            raise ValueError("Dataset Manager не инициализирован")

        try:
            # Загрузка dataset
            groups = self.orchestrator.dataset_manager.load_dataset()

            if not groups:
                raise ValueError("Dataset пуст или не загружен")

            # Валидация dataset
            validation_stats = self.orchestrator.data_validator.validate_dataset(groups)
            self.logger.info(f"📊 Валидация dataset: {validation_stats['valid_groups']} валидных групп")

            if validation_stats['valid_groups'] < 50:
                raise ValueError(f"Недостаточно валидных групп: {validation_stats['valid_groups']} (нужно минимум 50)")

            # Подготовка данных обучения
            features_batch, targets_batch = self.orchestrator.data_processor.prepare_training_data(groups)

            # Конвертируем SimpleDataBatch в DataBatch
            features_data_batch = DataBatch(
                data=features_batch.data,
                batch_id=features_batch.batch_id,
                data_type=DataType.TRAINING,
                metadata=features_batch.metadata
            )

            targets_data_batch = DataBatch(
                data=targets_batch.data,
                batch_id=targets_batch.batch_id,
                data_type=DataType.TRAINING,
                metadata=targets_batch.metadata
            )

            if features_data_batch.data.empty or targets_data_batch.data.empty:
                raise ValueError("Не удалось подготовить данные обучения")

            self.logger.info(f"✅ Подготовлены данные обучения: {len(features_data_batch.data)} примеров")

            return features_data_batch, targets_data_batch

        except Exception as e:
            self.logger.error(f"❌ Ошибка подготовки данных обучения: {e}")
            raise

    def create_prediction_features(self, recent_groups: List[str]) -> DataBatch:
        """Создание фич для предсказания через Data Processor"""
        if not self.orchestrator.data_processor:
            raise ValueError("Data Processor не инициализирован")

        try:
            # Валидация входных групп
            valid_groups = [group for group in recent_groups if self.orchestrator.data_validator.validate_group(group)]

            if not valid_groups:
                raise ValueError("Нет валидных групп для предсказания")

            # Создание фич
            prediction_simple_batch = self.orchestrator.data_processor.create_prediction_features(valid_groups)

            # Конвертируем SimpleDataBatch в DataBatch
            prediction_batch = DataBatch(
                data=prediction_simple_batch.data,
                batch_id=prediction_simple_batch.batch_id,
                data_type=DataType.PREDICTION,
                metadata=prediction_simple_batch.metadata
            )

            if prediction_batch.data.empty:
                raise ValueError("Не удалось создать фичи для предсказания")

            self.logger.info(f"✅ Созданы фичи для предсказания из {len(valid_groups)} групп")

            return prediction_batch

        except Exception as e:
            self.logger.error(f"❌ Ошибка создания фич предсказания: {e}")
            raise

    def add_new_data(self, new_groups: List[str]) -> bool:
        """Добавление новых данных в dataset"""
        if not self.orchestrator.dataset_manager:
            raise ValueError("Dataset Manager не инициализирован")

        try:
            # Валидация новых групп
            valid_groups = [group for group in new_groups if self.orchestrator.data_validator.validate_group(group)]

            if not valid_groups:
                self.logger.warning("⚠️ Нет валидных групп для добавления")
                return False

            # Добавление в dataset
            success = self.orchestrator.dataset_manager.add_groups(valid_groups)

            if success:
                self.logger.info(f"✅ Добавлено {len(valid_groups)} новых групп в dataset")

                # Обновление статистики
                stats = self.orchestrator.dataset_manager.get_dataset_stats()
                self.logger.info(f"📊 Обновленная статистика: {stats['valid_groups']} валидных групп")
            else:
                self.logger.error("❌ Не удалось добавить новые группы")

            return success

        except Exception as e:
            self.logger.error(f"❌ Ошибка добавления новых данных: {e}")
            return False

    def validate_prediction_accuracy(self, predictions: List[Tuple], actuals: List[List[int]]) -> Dict[str, Any]:
        """Валидация точности предсказаний через Data Validator"""
        if not self.orchestrator.data_validator:
            raise ValueError("Data Validator не инициализирован")

        return self.orchestrator.data_validator.analyze_prediction_accuracy(predictions, actuals)

    def backup_dataset(self) -> bool:
        """Создание бэкапа dataset"""
        if not self.orchestrator.dataset_manager:
            raise ValueError("Dataset Manager не инициализирован")

        return self.orchestrator.dataset_manager.backup_dataset()

    def get_data_processing_info(self) -> Dict[str, Any]:
        """Информация о data processing компонентах"""
        info = {
            "data_processor_initialized": self.orchestrator.data_processor is not None,
            "dataset_manager_initialized": self.orchestrator.dataset_manager is not None,
            "data_validator_initialized": self.orchestrator.data_validator is not None,
        }

        if self.orchestrator.data_processor:
            info.update(self.orchestrator.data_processor.get_feature_info())

        if self.orchestrator.dataset_manager:
            info.update(self.orchestrator.dataset_manager.get_dataset_stats())

        return info
