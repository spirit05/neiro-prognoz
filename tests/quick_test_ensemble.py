# /opt/model/tests/quick_test_ensemble.py
"""
БЫСТРЫЙ ТЕСТ ансамблевой системы
"""

import sys
import os
import numpy as np
import pandas as pd

sys.path.insert(0, '/opt/model')

from ml.core.types import DataBatch, TrainingConfig, DataType
from ml.ensemble import WeightedEnsemblePredictor, StatisticalPredictor, PatternBasedPredictor, FrequencyPredictor

def quick_test():
    """Быстрый тест основных функций"""
    print("🚀 БЫСТРЫЙ ТЕСТ АНСАМБЛЕВОЙ СИСТЕМЫ")
    
    # 1. Тест инициализации
    print("1. Тест инициализации...")
    ensemble = WeightedEnsemblePredictor("quick_test")
    statistical = StatisticalPredictor("statistical")
    pattern = PatternBasedPredictor("pattern")
    frequency = FrequencyPredictor("frequency")
    
    print("✅ Инициализация прошла успешно")
    
    # 2. Тест добавления предсказателей
    print("2. Тест добавления предсказателей...")
    ensemble.add_predictor("statistical", statistical, 0.4)
    ensemble.add_predictor("pattern", pattern, 0.3)
    ensemble.add_predictor("frequency", frequency, 0.3)
    
    assert len(ensemble.component_predictors) == 3
    assert ensemble.weights["statistical"] == 0.4
    print("✅ Добавление предсказателей прошло успешно")
    
    # 3. Тест обучения
    print("3. Тест обучения...")
    test_data = np.random.randint(1, 27, (20, 4))
    data_batch = DataBatch(
        data=pd.DataFrame(test_data),
        batch_id="test_batch",
        data_type=DataType.TRAINING
    )
    
    config = TrainingConfig(epochs=1)
    result = ensemble.train(data_batch, config)
    
    assert result.status.value == "trained"
    assert ensemble.is_trained
    print("✅ Обучение прошло успешно")
    
    # 4. Тест предсказания
    print("4. Тест предсказания...")
    pred_data = DataBatch(
        data=pd.DataFrame(np.random.randint(1, 27, (10, 4))),
        batch_id="pred_batch",
        data_type=DataType.PREDICTION
    )
    
    response = ensemble.predict(pred_data)
    
    assert isinstance(response.predictions, list)
    assert response.model_id == "quick_test"
    print("✅ Предсказание прошло успешно")
    
    # 5. Тест консистентности
    print("5. Тест консистентности...")
    response1 = ensemble.predict(pred_data)
    response2 = ensemble.predict(pred_data)
    
    assert len(response1.predictions) == len(response2.predictions)
    print("✅ Консистентность проверена")
    
    print("\n🎉 ВСЕ ТЕСТЫ ПРОЙДЕНЫ УСПЕШНО!")
    return True

if __name__ == "__main__":
    try:
        success = quick_test()
        sys.exit(0 if success else 1)
    except Exception as e:
        print(f"❌ ТЕСТ ПРОВАЛЕН: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
