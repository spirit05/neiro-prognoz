# /opt/model/tests/debug_ensemble.py
"""
ДИАГНОСТИКА ПРОБЛЕМ АНСАМБЛЕВОЙ СИСТЕМЫ
"""

import sys
import os
import numpy as np
import pandas as pd

sys.path.insert(0, '/opt/model')

from ml.core.types import DataBatch, TrainingConfig, DataType
from ml.ensemble import WeightedEnsemblePredictor, StatisticalPredictor, PatternBasedPredictor, FrequencyPredictor


def debug_data_extraction():
    """Диагностика извлечения данных из DataBatch"""
    print("🔍 ДИАГНОСТИКА ИЗВЛЕЧЕНИЯ ДАННЫХ")
    
    # Тестовые данные
    test_data = [
        [5, 12, 18, 23],
        [3, 8, 15, 21], 
        [7, 14, 19, 25],
        [2, 9, 16, 22],
        [6, 13, 20, 26]
    ]
    
    data_batch = DataBatch(
        data=pd.DataFrame(test_data),
        batch_id="debug_test",
        data_type=DataType.TRAINING
    )
    
    # Проверяем StatisticalPredictor
    statistical = StatisticalPredictor("debug_statistical")
    history = statistical._extract_history_from_batch(data_batch)
    print(f"📊 StatisticalPredictor извлек историю: {len(history)} чисел")
    print(f"  История: {history}")
    
    # Проверяем PatternBasedPredictor
    pattern = PatternBasedPredictor("debug_pattern")
    history_pattern = pattern._extract_history_from_batch(data_batch)
    print(f"🔍 PatternBasedPredictor извлек историю: {len(history_pattern)} чисел")
    
    # Проверяем FrequencyPredictor
    frequency = FrequencyPredictor("debug_frequency")
    dataset = frequency._extract_dataset_from_batch(data_batch)
    print(f"📈 FrequencyPredictor извлек датасет: {len(dataset)} групп")
    print(f"  Группы: {dataset}")


def debug_individual_predictors():
    """Диагностика индивидуальных предсказателей"""
    print("\n🔍 ДИАГНОСТИКА ИНДИВИДУАЛЬНЫХ ПРЕДСКАЗАТЕЛЕЙ")
    
    # Создаем более длинную историю для тестирования
    long_history = []
    for i in range(30):  # 30 примеров должно быть достаточно
        group = [
            np.random.randint(1, 27),
            np.random.randint(1, 27),
            np.random.randint(1, 27), 
            np.random.randint(1, 27)
        ]
        # Делаем группы валидными
        if group[0] == group[1]:
            group[1] = (group[1] % 26) + 1
        if group[2] == group[3]:
            group[3] = (group[3] % 26) + 1
        long_history.append(group)
    
    data_batch = DataBatch(
        data=pd.DataFrame(long_history),
        batch_id="long_history_train",
        data_type=DataType.TRAINING
    )
    
    # Тестируем StatisticalPredictor
    print("\n📊 StatisticalPredictor:")
    statistical = StatisticalPredictor("debug_statistical2")
    statistical.train(data_batch, TrainingConfig(epochs=2))
    
    # Проверяем предсказание на тех же данных
    response = statistical.predict(data_batch)
    print(f"  Прогнозов: {len(response.predictions)}")
    
    if response.predictions:
        print(f"  Пример прогноза: {response.predictions[0]}")
    else:
        print("  ❌ НЕТ ПРОГНОЗОВ!")
        # Проверим длину истории
        history = statistical._extract_history_from_batch(data_batch)
        print(f"  Длина истории: {len(history)}")
        print(f"  Требуется минимум: 20")
    
    # Тестируем PatternBasedPredictor
    print("\n🔍 PatternBasedPredictor:")
    pattern = PatternBasedPredictor("debug_pattern2")
    pattern.train(data_batch, TrainingConfig(epochs=2))
    
    response = pattern.predict(data_batch)
    print(f"  Прогнозов: {len(response.predictions)}")
    
    if response.predictions:
        print(f"  Пример прогноза: {response.predictions[0]}")
    else:
        print("  ❌ НЕТ ПРОГНОЗОВ!")
        history = pattern._extract_history_from_batch(data_batch)
        print(f"  Длина истории: {len(history)}")
        print(f"  Требуется минимум: 15")
    
    # Тестируем FrequencyPredictor
    print("\n📈 FrequencyPredictor:")
    frequency = FrequencyPredictor("debug_frequency2")
    frequency.train(data_batch, TrainingConfig(epochs=2))
    
    response = frequency.predict(data_batch)
    print(f"  Прогнозов: {len(response.predictions)}")
    
    if response.predictions:
        print(f"  Пример прогноза: {response.predictions[0]}")
    else:
        print("  ❌ НЕТ ПРОГНОЗОВ!")
        print(f"  Проанализировано групп: {frequency.total_groups}")


def debug_with_simple_data():
    """Тест с простыми данными, которые гарантированно должны работать"""
    print("\n🔍 ТЕСТ С ПРОСТЫМИ ДАННЫМИ")
    
    # Создаем простые последовательные данные
    simple_data = []
    for i in range(25):  # 25 групп
        base = (i % 20) + 1
        group = [base, base + 1, base + 2, base + 3]
        # Корректируем числа в диапазон 1-26
        group = [max(1, min(26, x)) for x in group]
        # Исправляем пары если нужно
        if group[0] == group[1]:
            group[1] = (group[1] % 26) + 1
        if group[2] == group[3]:
            group[3] = (group[3] % 26) + 1
        simple_data.append(group)
    
    data_batch = DataBatch(
        data=pd.DataFrame(simple_data),
        batch_id="simple_data_train", 
        data_type=DataType.TRAINING
    )
    
    # Тестируем StatisticalPredictor
    statistical = StatisticalPredictor("simple_statistical")
    statistical.train(data_batch, TrainingConfig(epochs=2))
    
    # Создаем данные для предсказания (длинная история)
    pred_history = list(range(1, 21))  # 20 чисел - достаточно для StatisticalPredictor
    pred_batch = DataBatch(
        data=pd.DataFrame([pred_history]),  # Одна строка с 20 числами
        batch_id="simple_pred",
        data_type=DataType.PREDICTION
    )
    
    response = statistical.predict(pred_batch)
    print(f"📊 StatisticalPredictor с простыми данными: {len(response.predictions)} прогнозов")
    
    if response.predictions:
        print(f"  Пример: {response.predictions[0]}")
    else:
        print("  ❌ ВСЕ ЕЩЕ НЕТ ПРОГНОЗОВ!")
        
        # Детальная диагностика
        history = statistical._extract_history_from_batch(pred_batch)
        print(f"  Извлеченная история: {history}")
        print(f"  Длина истории: {len(history)}")
        
        # Проверим анализатор паттернов
        analyzer = statistical._get_pattern_analyzer()
        if analyzer:
            patterns = analyzer.analyze_time_series(history)
            print(f"  Паттерны: {patterns}")
        else:
            print("  ❌ Анализатор паттернов не загружен!")


if __name__ == "__main__":
    print("🚀 ЗАПУСК ДИАГНОСТИКИ АНСАМБЛЕВОЙ СИСТЕМЫ")
    print("=" * 50)
    
    debug_data_extraction()
    debug_individual_predictors() 
    debug_with_simple_data()
    
    print("\n" + "=" * 50)
    print("🔚 ДИАГНОСТИКА ЗАВЕРШЕНА")
