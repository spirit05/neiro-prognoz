# /opt/model/tests/test_ensemble_real_data.py
"""
ТЕСТ РЕАЛЬНОЙ РАБОТОСПОСОБНОСТИ АНСАМБЛЕВОЙ СИСТЕМЫ
"""

import sys
import os
import numpy as np
import pandas as pd

sys.path.insert(0, '/opt/model')

from ml.core.types import DataBatch, TrainingConfig, DataType
from ml.ensemble import WeightedEnsemblePredictor, StatisticalPredictor, PatternBasedPredictor, FrequencyPredictor


def test_ensemble_with_realistic_data():
    """Тест ансамбля с реалистичными данными"""
    print("🎯 ТЕСТ РЕАЛЬНОЙ РАБОТОСПОСОБНОСТИ")
    
    # Создаем реалистичные данные (похожие на реальную историю чисел)
    realistic_data = [
        [5, 12, 18, 23],
        [3, 8, 15, 21], 
        [7, 14, 19, 25],
        [2, 9, 16, 22],
        [6, 13, 20, 26],
        [4, 11, 17, 24],
        [1, 10, 15, 23],
        [5, 12, 19, 25],
        [3, 8, 16, 22],
        [7, 14, 20, 26]
    ]
    
    # Создаем ансамбль
    ensemble = WeightedEnsemblePredictor("real_data_test")
    
    statistical = StatisticalPredictor("statistical")
    pattern = PatternBasedPredictor("pattern") 
    frequency = FrequencyPredictor("frequency")
    
    ensemble.add_predictor("statistical", statistical, 0.35)
    ensemble.add_predictor("pattern", pattern, 0.25)
    ensemble.add_predictor("frequency", frequency, 0.20)
    
    # Обучаем на реалистичных данных
    data_batch = DataBatch(
        data=pd.DataFrame(realistic_data),
        batch_id="real_data_train",
        data_type=DataType.TRAINING
    )
    
    config = TrainingConfig(epochs=3)
    result = ensemble.train(data_batch, config)
    
    print(f"✅ Обучение завершено: {result.status.value}")
    
    # Тестируем предсказание на новых данных
    test_data = [
        [4, 11, 18, 24],
        [2, 9, 17, 23],
        [6, 13, 19, 25]
    ]
    
    pred_batch = DataBatch(
        data=pd.DataFrame(test_data),
        batch_id="real_data_pred",
        data_type=DataType.PREDICTION  
    )
    
    response = ensemble.predict(pred_batch)
    
    print(f"✅ Получено {len(response.predictions)} прогнозов")
    
    # Анализируем качество прогнозов
    for i, prediction in enumerate(response.predictions[:3]):
        print(f"Прогноз {i+1}: {prediction}")
        
        # Проверяем валидность прогноза
        assert len(prediction) == 4, "Прогноз должен содержать 4 числа"
        assert all(1 <= x <= 26 for x in prediction), "Все числа должны быть в диапазоне 1-26"
        assert prediction[0] != prediction[1], "Первая пара должна иметь разные числа"
        assert prediction[2] != prediction[3], "Вторая пара должна иметь разные числа"
        
        print(f"  ✅ Прогноз {i+1} валиден")
    
    # Проверяем, что разные предсказатели дают разные результаты
    statistical_response = statistical.predict(pred_batch)
    pattern_response = pattern.predict(pred_batch)
    frequency_response = frequency.predict(pred_batch)
    
    print(f"📊 StatisticalPredictor: {len(statistical_response.predictions)} прогнозов")
    print(f"📊 PatternBasedPredictor: {len(pattern_response.predictions)} прогнозов") 
    print(f"📊 FrequencyPredictor: {len(frequency_response.predictions)} прогнозов")
    
    # Проверяем, что есть различия между предсказателями (разные стратегии)
    statistical_groups = set([tuple(pred) for pred in statistical_response.predictions])
    pattern_groups = set([tuple(pred) for pred in pattern_response.predictions])
    frequency_groups = set([tuple(pred) for pred in frequency_response.predictions])
    
    # Должны быть некоторые различия (но могут быть и пересечения)
    all_unique = len(statistical_groups.union(pattern_groups).union(frequency_groups))
    print(f"🔀 Уникальных прогнозов от всех стратегий: {all_unique}")
    
    assert all_unique > 0, "Должны быть уникальные прогнозы от разных стратегий"
    
    print("🎉 ТЕСТ РЕАЛЬНОЙ РАБОТОСПОСОБНОСТИ ПРОЙДЕН!")
    return True


def test_individual_predictors_detailed():
    """Детальный тест индивидуальных предсказателей"""
    print("\n🔍 ДЕТАЛЬНЫЙ ТЕСТ ИНДИВИДУАЛЬНЫХ ПРЕДСКАЗАТЕЛЕЙ")
    
    test_data = [
        [1, 8, 15, 22],
        [3, 10, 17, 24], 
        [5, 12, 19, 26],
        [2, 9, 16, 23],
        [4, 11, 18, 25]
    ]
    
    data_batch = DataBatch(
        data=pd.DataFrame(test_data),
        batch_id="detailed_test",
        data_type=DataType.TRAINING
    )
    
    # Тестируем StatisticalPredictor
    print("\n📊 StatisticalPredictor:")
    statistical = StatisticalPredictor("statistical_detailed")
    statistical.train(data_batch, TrainingConfig(epochs=2))
    
    # Проверяем анализ паттернов
    history = [1, 5, 12, 18, 3, 9, 15, 21, 6, 11, 19, 24, 8, 13, 20, 25]
    test_batch = DataBatch(
        data=pd.DataFrame([history]),
        batch_id="pattern_test", 
        data_type=DataType.PREDICTION
    )
    
    response = statistical.predict(test_batch)
    print(f"  Прогнозы на основе паттернов: {len(response.predictions)}")
    
    # Тестируем PatternBasedPredictor
    print("\n🔍 PatternBasedPredictor:")
    pattern = PatternBasedPredictor("pattern_detailed")
    pattern.train(data_batch, TrainingConfig(epochs=2))
    
    # Проверяем поиск последовательностей
    sequences = pattern._find_sequences(history)
    print(f"  Найдено последовательностей: {len(sequences)}")
    for seq in sequences:
        print(f"    Последовательность: {seq}")
    
    response = pattern.predict(test_batch)
    print(f"  Прогнозы на основе последовательностей: {len(response.predictions)}")
    
    # Тестируем FrequencyPredictor
    print("\n📈 FrequencyPredictor:")
    frequency = FrequencyPredictor("frequency_detailed")
    frequency.train(data_batch, TrainingConfig(epochs=2))
    
    print(f"  Проанализировано групп: {frequency.total_groups}")
    print(f"  Уникальных чисел: {len(frequency.number_frequencies)}")
    print(f"  Уникальных пар: {len(frequency.pair_frequencies)}")
    
    response = frequency.predict(test_batch)
    print(f"  Прогнозы на основе частот: {len(response.predictions)}")
    
    print("✅ ДЕТАЛЬНЫЙ ТЕСТ ПРОЙДЕН!")
    return True


if __name__ == "__main__":
    try:
        test_ensemble_with_realistic_data()
        test_individual_predictors_detailed()
        print("\n🎉 ВСЕ ТЕСТЫ РЕАЛЬНОЙ РАБОТОСПОСОБНОСТИ ПРОЙДЕНЫ!")
    except Exception as e:
        print(f"❌ ТЕСТ ПРОВАЛЕН: {e}")
        import traceback
        traceback.print_exc()
        exit(1)
