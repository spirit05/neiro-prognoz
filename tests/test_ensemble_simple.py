# /opt/model/tests/test_ensemble_simple.py
"""
УПРОЩЕННЫЙ ТЕСТ АНСАМБЛЕВОЙ СИСТЕМЫ
"""

import sys
import os
import numpy as np
import pandas as pd

sys.path.insert(0, '/opt/model')

from ml.core.types import DataBatch, TrainingConfig, DataType
from ml.ensemble import WeightedEnsemblePredictor, StatisticalPredictor, PatternBasedPredictor, FrequencyPredictor


def test_ensemble_simple():
    """Упрощенный тест ансамбля"""
    print("🎯 УПРОЩЕННЫЙ ТЕСТ АНСАМБЛЕВОЙ СИСТЕМЫ")
    
    # Создаем очень простые данные
    simple_data = []
    for i in range(30):  # 30 групп
        # Простая последовательность
        base = (i % 10) + 1
        group = [base, base + 5, base + 10, base + 15]
        # Корректируем в диапазон 1-26
        group = [max(1, min(26, x)) for x in group]
        simple_data.append(group)
    
    print(f"📊 Создано {len(simple_data)} тестовых групп")
    
    # Создаем ансамбль
    ensemble = WeightedEnsemblePredictor("simple_test")
    
    statistical = StatisticalPredictor("simple_statistical")
    pattern = PatternBasedPredictor("simple_pattern")
    frequency = FrequencyPredictor("simple_frequency")
    
    ensemble.add_predictor("statistical", statistical, 0.35)
    ensemble.add_predictor("pattern", pattern, 0.25)
    ensemble.add_predictor("frequency", frequency, 0.20)
    
    # Обучаем
    data_batch = DataBatch(
        data=pd.DataFrame(simple_data),
        batch_id="simple_train",
        data_type=DataType.TRAINING
    )
    
    config = TrainingConfig(epochs=2)
    result = ensemble.train(data_batch, config)
    print(f"✅ Обучение завершено: {result.status.value}")
    
    # Для предсказания используем длинную историю
    pred_history = list(range(1, 31))  # 30 чисел
    pred_batch = DataBatch(
        data=pd.DataFrame([pred_history]),  # Одна строка с историей
        batch_id="simple_pred",
        data_type=DataType.PREDICTION
    )
    
    # Тестируем индивидуальные предсказатели
    print("\n🔍 ТЕСТ ИНДИВИДУАЛЬНЫХ ПРЕДСКАЗАТЕЛЕЙ:")
    
    statistical_response = statistical.predict(pred_batch)
    print(f"📊 StatisticalPredictor: {len(statistical_response.predictions)} прогнозов")
    
    pattern_response = pattern.predict(pred_batch) 
    print(f"🔍 PatternBasedPredictor: {len(pattern_response.predictions)} прогнозов")
    
    frequency_response = frequency.predict(pred_batch)
    print(f"📈 FrequencyPredictor: {len(frequency_response.predictions)} прогнозов")
    
    # Тестируем ансамбль
    ensemble_response = ensemble.predict(pred_batch)
    print(f"🎯 Ensemble: {len(ensemble_response.predictions)} прогнозов")
    
    # Выводим примеры прогнозов
    if statistical_response.predictions:
        print(f"📊 Statistical пример: {statistical_response.predictions[0]}")
    if pattern_response.predictions:
        print(f"🔍 Pattern пример: {pattern_response.predictions[0]}")
    if frequency_response.predictions:
        print(f"📈 Frequency пример: {frequency_response.predictions[0]}")
    if ensemble_response.predictions:
        print(f"🎯 Ensemble пример: {ensemble_response.predictions[0]}")
    
    # Проверяем, что хотя бы один предсказатель работает
    total_predictions = (len(statistical_response.predictions) + 
                        len(pattern_response.predictions) + 
                        len(frequency_response.predictions))
    
    # 🔧 ИСПРАВЛЕНИЕ: используем assert вместо return
    assert total_predictions > 0, "Ни один предсказатель не сгенерировал прогнозы"
    print(f"🎉 ТЕСТ ПРОЙДЕН! Всего прогнозов: {total_predictions}")


if __name__ == "__main__":
    try:
        test_ensemble_simple()
        print("\n🎉 ТЕСТ УСПЕШНО ЗАВЕРШЕН!")
        sys.exit(0)
    except Exception as e:
        print(f"\n❌ ТЕСТ ПРОВАЛЕН: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

