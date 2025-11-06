#!/usr/bin/env python3
"""
ТЕСТ ЭТАПА 1 - КОНФИГУРАЦИОННАЯ СИСТЕМА (DEV СРЕДА)
Запуск: python3 /opt/dev/test_config_stage1.py
"""

import sys
import os

def test_configuration_system():
    """Тестирование конфигурационной системы ЭТАПА 1 в DEV среде"""
    print("🧪 ТЕСТ КОНФИГУРАЦИОННОЙ СИСТЕМЫ - ЭТАП 1 (DEV СРЕДА)")
    print("=" * 60)
    
    # Сначала проверяем, в какой среде работаем
    dev_path = "/opt/dev"
    prod_path = "/opt/project"
    
    if os.path.exists(dev_path):
        print(f"🚀 РЕЖИМ: DEV среда ({dev_path})")
        working_path = dev_path
    elif os.path.exists(prod_path):
        print(f"📦 РЕЖИМ: PROD среда ({prod_path})")
        working_path = prod_path
    else:
        print("❌ Ни DEV, ни PROD среды не найдены!")
        return False
    
    try:
        # 1. ПРОВЕРКА СТРУКТУРЫ ДИРЕКТОРИЙ
        print("\n1. 📁 Проверка структуры директорий...")
        expected_dirs = [
            f'{working_path}',
            f'{working_path}/config',
            f'{working_path}/ml',
            f'{working_path}/ml/core',
            f'{working_path}/ml/ensemble', 
            f'{working_path}/ml/features',
            f'{working_path}/ml/learning',
            f'{working_path}/ml/utils',
            f'{working_path}/services',
            f'{working_path}/services/auto_learning',
            f'{working_path}/services/telegram', 
            f'{working_path}/services/monitoring',
            f'{working_path}/web',
            f'{working_path}/data',
            f'{working_path}/data/datasets',
            f'{working_path}/data/models',
            f'{working_path}/data/analytics',
            f'{working_path}/data/logs',
            f'{working_path}/tests'
        ]
        
        missing_dirs = []
        for dir_path in expected_dirs:
            if os.path.exists(dir_path):
                print(f"   ✅ {dir_path}")
            else:
                print(f"   ❌ {dir_path} - НЕ СУЩЕСТВУЕТ!")
                missing_dirs.append(dir_path)
        
        if missing_dirs:
            print(f"   ⚠️  Отсутствует директорий: {len(missing_dirs)}")
            # Автоматически создаем недостающие директории
            for dir_path in missing_dirs:
                os.makedirs(dir_path, exist_ok=True)
                print(f"   📁 Создана: {dir_path}")
        
        # 2. ПРОВЕРКА КОНФИГУРАЦИОННЫХ ФАЙЛОВ
        print("\n2. ⚙️ Проверка конфигурационных файлов...")
        config_files = [
            f'{working_path}/config/__init__.py',
            f'{working_path}/config/paths.py', 
            f'{working_path}/config/constants.py',
            f'{working_path}/config/logging_config.py',
            f'{working_path}/config/security.py'
        ]
        
        missing_files = []
        for file_path in config_files:
            if os.path.exists(file_path):
                print(f"   ✅ {file_path}")
            else:
                print(f"   ❌ {file_path} - НЕ СУЩЕСТВУЕТ!")
                missing_files.append(file_path)
        
        if missing_files:
            print(f"   ❌ Отсутствует файлов: {len(missing_files)}")
            return False
        
        # 3. ТЕСТ ИМПОРТА КОНФИГУРАЦИИ
        print("\n3. 🔄 Тест импорта конфигурационных модулей...")
        
        # Добавляем путь к конфигурации
        sys.path.insert(0, working_path)
        
        try:
            from config import paths, constants, logging_config, security
            print("   ✅ Импорт config.paths - УСПЕХ")
            print("   ✅ Импорт config.constants - УСПЕХ") 
            print("   ✅ Импорт config.logging_config - УСПЕХ")
            print("   ✅ Импорт config.security - УСПЕХ")
        except ImportError as e:
            print(f"   ❌ Ошибка импорта: {e}")
            return False
        
        # 4. ТЕСТ ПУТЕЙ И СРЕДЫ
        print("\n4. 📍 Тест системы путей и среды...")
        print(f"   🎯 Текущая среда: {'DEV' if working_path == dev_path else 'PROD'}")
        print(f"   📁 PROJECT_ROOT: {paths.PROJECT_ROOT}")
        print(f"   📁 DATASET_FILE: {paths.DATASET_FILE}")
        print(f"   📁 MODEL_FILE: {paths.MODEL_FILE}")
        
        # Проверяем, что пути указывают на правильную среду
        if str(paths.PROJECT_ROOT) != working_path:
            print(f"   ❌ Несоответствие путей! Ожидалось: {working_path}, получено: {paths.PROJECT_ROOT}")
            return False
        else:
            print("   ✅ Пути соответствуют выбранной среде")
        
        # 5. ТЕСТ КОНСТАНТ
        print("\n5. 🔧 Тест констант...")
        print(f"   MAX_API_RETRIES: {constants.MAX_API_RETRIES}")
        print(f"   SCHEDULE_MINUTES: {constants.SCHEDULE_MINUTES}")
        print(f"   PREDICTION_TOP_K: {constants.PREDICTION_TOP_K}")
        print(f"   BUFFER_MINUTES: {constants.BUFFER_MINUTES}")
        print(f"   CRITICAL_INTERVAL: {constants.CRITICAL_INTERVAL_MINUTES}")
        
        # 6. ТЕСТ ЛОГИРОВАНИЯ
        print("\n6. 📝 Тест системы логирования...")
        try:
            logger = logging_config.get_ml_system_logger()
            logger.info("✅ Тестовое сообщение от ML системы")
            print("   ✅ Логирование работает")
            
            # Проверяем создание лог-файла
            log_file = paths.LOGS_DIR / "ml_system.log"
            if log_file.exists():
                print(f"   ✅ Лог-файл создан: {log_file}")
            else:
                print(f"   ⚠️  Лог-файл не создан: {log_file}")
                
        except Exception as e:
            print(f"   ❌ Ошибка логирования: {e}")
            return False
        
        # 7. ТЕСТ БЕЗОПАСНОСТИ
        print("\n7. 🛡️ Тест системы безопасности...")
        
        # Валидация данных
        validator = security.DataValidator()
        test_cases = [
            ("12 26 26 11", True),
            ("1 2 3", False),  # мало чисел
            ("1 2 3 4 5", False),  # много чисел  
            ("0 1 2 3", False),  # число вне диапазона
            ("1 2 3 27", False),  # число вне диапазона
            ("abc def ghi jkl", False)  # не числа
        ]
        
        all_valid = True
        for test_input, expected in test_cases:
            result = validator.validate_group(test_input)
            status = "✅" if result == expected else "❌"
            print(f"   {status} '{test_input}' -> {result} (ожидалось: {expected})")
            if result != expected:
                all_valid = False
        
        if not all_valid:
            print("   ❌ Тесты валидации не пройдены")
            return False
        
        # Защитные механизмы
        protection = security.ServiceProtection()
        test_cases = [
            (1.5, "critical"),
            (5.0, "buffer"), 
            (10.0, "normal")
        ]
        
        for minutes, expected_status in test_cases:
            result = protection.check_time_slot_buffer(minutes)
            status = "✅" if result['status'] == expected_status else "❌"
            print(f"   {status} {minutes} мин -> {result['status']} (ожидалось: {expected_status})")
        
        # 8. ТЕСТ БЕЗОПАСНЫХ ФАЙЛОВЫХ ОПЕРАЦИЙ
        print("\n8. 💾 Тест безопасных файловых операций...")
        try:
            test_data = {"test": "data", "timestamp": "2024-01-01", "environment": "DEV"}
            test_file = paths.LOGS_DIR / "test_config.json"
            
            # Запись
            success_write = security.SafeFileOperations.write_json_safe(test_file, test_data)
            print(f"   ✅ Запись файла: {success_write}")
            
            # Чтение
            read_data = security.SafeFileOperations.read_json_safe(test_file)
            if read_data and read_data.get("environment") == "DEV":
                print(f"   ✅ Чтение файла: данные корректны")
            else:
                print(f"   ❌ Ошибка чтения данных")
                return False
            
            # Очистка
            if test_file.exists():
                test_file.unlink()
                print(f"   ✅ Очистка тестового файла")
                
        except Exception as e:
            print(f"   ❌ Ошибка файловых операций: {e}")
            return False
        
        print("\n" + "=" * 60)
        print("🎉 ВСЕ ТЕСТЫ ЭТАПА 1 ПРОЙДЕНЫ УСПЕШНО!")
        print(f"✅ Конфигурационная система готова в {working_path}")
        print("➡️  Можете переходить к ЭТАПУ 2 - ML СИСТЕМА ЯДРО")
        
        return True
        
    except Exception as e:
        print(f"\n❌ КРИТИЧЕСКАЯ ОШИБКА ТЕСТИРОВАНИЯ: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = test_configuration_system()
    sys.exit(0 if success else 1)