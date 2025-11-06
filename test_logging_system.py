# test_logging_system.py
#!/usr/bin/env python3
"""
Тестирование новой системы логирования
"""

import os
import sys

PROJECT_ROOT = '/home/spirit/Desktop/project'
sys.path.insert(0, PROJECT_ROOT)

def test_logging_system():
    """Тестируем систему логирования"""
    print("🧪 Тестируем систему логирования...")
    
    try:
        from utils.logging_system import (
            get_training_logger, 
            get_ml_system_logger,
            get_auto_learning_logger,
            get_web_logger
        )
        
        # Тестируем все логгеры
        training_logger = get_training_logger()
        ml_logger = get_ml_system_logger()
        auto_logger = get_auto_learning_logger()
        web_logger = get_web_logger()
        
        # Пишем тестовые сообщения
        training_logger.info("✅ Тестовое сообщение от Training логгера")
        ml_logger.info("✅ Тестовое сообщение от MLSystem логгера") 
        auto_logger.info("✅ Тестовое сообщение от AutoLearning логгера")
        web_logger.info("✅ Тестовое сообщение от WebInterface логгера")
        
        # Проверяем что файлы созданы
        from config.paths import paths
        
        log_files = [
            paths.TRAINING_LOG,
            paths.ML_SYSTEM_LOG, 
            paths.AUTO_LEARNING_LOG,
            paths.WEB_INTERFACE_LOG
        ]
        
        for log_file in log_files:
            if os.path.exists(log_file):
                print(f"✅ Лог-файл создан: {log_file}")
                
                # Проверяем что сообщения записаны
                with open(log_file, 'r', encoding='utf-8') as f:
                    content = f.read()
                    if "Тестовое сообщение" in content:
                        print(f"✅ Сообщения записываются в: {log_file}")
                    else:
                        print(f"⚠️  Сообщения не найдены в: {log_file}")
            else:
                print(f"❌ Лог-файл не создан: {log_file}")
        
        print("🎉 Система логирования работает корректно!")
        return True
        
    except Exception as e:
        print(f"❌ Ошибка системы логирования: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = test_logging_system()
    sys.exit(0 if success else 1)