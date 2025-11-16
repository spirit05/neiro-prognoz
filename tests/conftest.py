# /opt/model/tests/conftest.py
"""
Конфигурация pytest для тестов новой архитектуры
"""
import pytest
import sys
import os

# Добавляем корневую директорию проекта в Python path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

@pytest.fixture
def sample_data_batch():
    """Фикстура для создания тестового DataBatch"""
    from ml.core.types import DataBatch, DataType
    import pandas as pd
    
    data = pd.DataFrame({
        'feature1': [1, 2, 3, 4, 5],
        'feature2': [0.1, 0.2, 0.3, 0.4, 0.5],
        'target': [0, 1, 0, 1, 0]
    })
    
    return DataBatch(
        data=data,
        batch_id="test_batch",
        data_type=DataType.TRAINING
    )

@pytest.fixture
def sample_prediction_response():
    """Фикстура для создания тестового PredictionResponse"""
    from ml.core.types import PredictionResponse
    from datetime import datetime
    
    return PredictionResponse(
        predictions=[[1, 2, 3, 4], [5, 6, 7, 8]],
        model_id="test_model",
        inference_time=0.1,
        timestamp=datetime.now()
    )

@pytest.fixture
def sample_analysis_result():
    """Фикстура для создания тестового AnalysisResult (для ЭТАПА 6)"""
    from ml.core.types import AnalysisResult
    from datetime import datetime
    
    return AnalysisResult(
        timestamp=datetime.now().isoformat(),
        performance_metrics={'overall_accuracy': 0.75},
        error_patterns={'common_errors': {'no_matches': 2}},
        recommendations={'training_suggestions': ['Test recommendation']},
        ensemble_weights={'model1': 0.5, 'model2': 0.5}
    )
