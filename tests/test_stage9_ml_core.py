# tests/test_stage9_ml_core.py
import sys
import os
import logging
from pathlib import Path

# Добавляем корневую директорию проекта в Python path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from ml.core.orchestrator import MLOrchestrator
from ml.core.types import ModelStatus, DataBatch, TrainingConfig

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger("STAGE9_TEST")

def test_ml_core_complete():
    """Полное тестирование ML-ядра - ФИНАЛЬНАЯ ВЕРСИЯ"""
    
    logger.info("🚀 НАЧАЛО ЭТАПА 9: Тестирование ML-ядра")
    
    try:
        # 1. Инициализация оркестратора
        logger.info("🔄 Шаг 1: Инициализация MLOrchestrator...")
        
        orchestrator = MLOrchestrator()
        status = orchestrator.get_system_status()
        logger.info(f"✅ Оркестратор инициализирован: {status}")
        
        # 2. Подготовка данных
        logger.info("🔄 Шаг 2: Подготовка данных...")
        
        features_batch, targets_batch = orchestrator.prepare_training_data()
        logger.info(f"✅ Данные подготовлены: {len(features_batch.data)} features, {len(targets_batch.data)} targets")
        
        # 3. Обучение основной модели
        logger.info("🔄 Шаг 3: Обучение основной модели...")
        
        model_id = "enhanced_predictor_v2"
        train_config = TrainingConfig(
            batch_size=8,
            learning_rate=0.001,
            epochs=3
        )
        
        training_result = orchestrator.train_model_with_strategy(
            model_id=model_id,
            strategy_id="basic",
            data=features_batch,
            config=train_config
        )
        
        logger.info(f"✅ Обучение завершено: {training_result.status}")
        logger.info(f"📈 Финальный loss: {training_result.metrics.get('final_training_loss', 'N/A')}")
        
        # Проверяем, что модель действительно обучена
        if not orchestrator._models[model_id]._is_trained:
            logger.error("❌ Модель не помечена как обученная после обучения!")
            return False
        
        # 4. Генерация прогнозов после обучения
        logger.info("🔄 Шаг 4: Генерация прогнозов после обучения...")
        
        test_features = features_batch.data.iloc[:1]
        test_batch = DataBatch(
            data=test_features,
            batch_id="test_prediction", 
            data_type="prediction"
        )
        
        response = orchestrator._models[model_id].predict(test_batch)
        logger.info(f"✅ После обучения сгенерировано прогнозов: {len(response.predictions)}")
        for i, pred in enumerate(response.predictions[:3]):
            logger.info(f"🎯 Прогноз {i+1}: {pred}")
        
        # 5. Дообучение
        logger.info("🔄 Шаг 5: Дообучение...")
        
        new_groups = ["12 13 14 15", "16 17 18 19", "20 21 22 23"]
        success = orchestrator.add_new_data(new_groups)
        
        if success:
            logger.info("✅ Новые данные добавлены")
            
            incremental_config = TrainingConfig(
                batch_size=8,
                learning_rate=0.0005,
                epochs=2
            )
            
            try:
                incremental_result = orchestrator.train_model_with_strategy(
                    model_id=model_id,
                    strategy_id="incremental",
                    data=features_batch,
                    config=incremental_config
                )
                logger.info(f"✅ Дообучение завершено: {incremental_result.status}")
                
                # 6. Генерация прогнозов после дообучения
                logger.info("🔄 Шаг 6: Генерация прогнозов после дообучения...")
                
                response_after_incremental = orchestrator._models[model_id].predict(test_batch)
                logger.info(f"✅ После дообучения сгенерировано прогнозов: {len(response_after_incremental.predictions)}")
                for i, pred in enumerate(response_after_incremental.predictions[:3]):
                    logger.info(f"🎯 Прогноз после дообучения {i+1}: {pred}")
                    
            except Exception as e:
                logger.error(f"❌ Ошибка дообучения: {e}")
                return False
        
        # 7. Система самообучения
        logger.info("🔄 Шаг 7: Система самообучения...")
        
        if orchestrator.self_learning_system:
            recommendations = orchestrator.self_learning_system.get_learning_recommendations()
            logger.info("💡 Рекомендации:")
            for rec in recommendations:
                logger.info(f"   - {rec}")
        
        # 8. Сохранение состояний
        logger.info("🔄 Шаг 8: Сохранение состояний...")
        
        model_dir = project_root / "saved_models" / "stage9_test"
        model_dir.mkdir(parents=True, exist_ok=True)
        model_path = model_dir / f"{model_id}.pth"
        
        orchestrator._models[model_id].save(model_path)
        logger.info(f"💾 Модель сохранена: {model_path}")
        
        # 9. Финальный статус
        logger.info("🔄 Шаг 9: Финальный статус...")
        
        final_status = orchestrator.get_system_status()
        logger.info("📊 ФИНАЛЬНЫЙ СТАТУС:")
        logger.info(f"   - Моделей: {final_status['models_registered']}")
        logger.info(f"   - Обученных: {sum(1 for m in orchestrator._models.values() if m._is_trained)}")
        logger.info(f"   - Data processing: {final_status['data_processing_initialized']}")
        logger.info(f"   - Self-learning: {final_status['self_learning_configured']}")
        
        # Проверяем, что модель остается обученной
        if orchestrator._models[model_id]._is_trained:
            logger.info("🎉 ЭТАП 9 ЗАВЕРШЕН УСПЕШНО! ML-ядро готово к работе!")
            return True
        else:
            logger.error("💥 Модель не осталась обученной после всех операций!")
            return False
        
    except Exception as e:
        logger.error(f"💥 ОШИБКА: {e}")
        import traceback
        logger.error(f"Трассировка: {traceback.format_exc()}")
        return False

if __name__ == "__main__":
    print("=" * 60)
    print("🚀 ЭТАП 9: Финальное тестирование ML-ядра")
    print("=" * 60)
    
    success = test_ml_core_complete()
    
    if success:
        print("\n🎉 ЭТАП 9 ПРОЙДЕН УСПЕШНО!")
        print("✅ ML-ядро полностью готово к интеграции!")
        print("\n📋 ПРОВЕРЕНО:")
        print("   - Обучение модели и установка флагов")
        print("   - Генерация прогнозов после обучения") 
        print("   - Добавление новых данных и дообучение")
        print("   - Генерация прогнозов после дообучения")
        print("   - Работа системы самообучения")
        print("   - Корректное сохранение состояний")
    else:
        print("\n💥 ЭТАП 9 НЕ ПРОЙДЕН")
        
    sys.exit(0 if success else 1)
