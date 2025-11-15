import pytest
import pandas as pd
import numpy as np
from ml.core.types import DataBatch, DataType

@pytest.fixture
def create_data_batch():
    """Фикстура для создания DataBatch с DataFrame"""
    def _create_batch(data, batch_id="test", data_type=DataType.TRAINING):
        # Гарантируем что data это DataFrame
        if isinstance(data, np.ndarray):
            data = pd.DataFrame(data)
        elif isinstance(data, list):
            data = pd.DataFrame(data)
        return DataBatch(
            data=data,
            batch_id=batch_id,
            data_type=data_type
        )
    return _create_batch
