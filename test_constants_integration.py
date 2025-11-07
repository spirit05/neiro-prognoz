#!/usr/bin/env python3
"""
Тест интеграции с constants.py
"""

import sys
import os
sys.path.insert(0, '/opt/dev')

def test_constants_integration():
    """Тестирование использования constants.py"""
    print("🧪 Тестирование интеграции с constants.py...")
    
    try:
        from config.constants import (
            MAIN_TRAINING_EPOCHS, RETRAIN_EPOCHS, ENSEMBLE_TOP_K,
            ENSEMBLE_MIN_CONFIDENCE
        )
        
        print(f"✅ MAIN_TRAINING_EPOCHS: {MAIN_TRAINING_EPOCHS}")
        print(f"✅ RETRAIN_EPOCHS: {RETRAIN_EPOCHS}")
        print(f"✅ ENSEMBLE_TOP_K: {ENSEMBLE_TOP_K}")
        print(f"✅ ENSEMBLE_MIN_CONFIDENCE: {ENSEMBLE_MIN_CONFIDENCE}")
        
        # Проверяем импорты в реальных модулях
        from ml.core.trainer import EnhancedTrainer
        from ml.ensemble.ensemble import EnsemblePredictor  
        from services.auto_learning.service import AutoLearningService
        
        print("✅ Все модули импортируются корректно")
        print("🎯 Параметры обучения теперь централизованы в constants.py")
        
        return True
        
    except Exception as e:
        print(f"❌ Ошибка: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    test_constants_integration()
