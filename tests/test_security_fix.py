# [file name]: tests/test_security_fix.py
"""
Тест исправления security.py
"""

import sys
sys.path.insert(0, '/opt/dev')

def test_security_imports():
    """Тест импортов из security.py"""
    print("🔍 ТЕСТ ИМПОРТОВ SECURITY...")
    
    try:
        from config.security import (
            FileLock,
            SafeFileOperations, 
            DataValidator,
            ServiceProtection,
            SecurityManager
        )
        print("✅ Все классы security импортируются")
        
        # Проверяем создание объектов
        file_lock = FileLock("/tmp/test.txt")
        safe_ops = SafeFileOperations()
        validator = DataValidator()
        service_protection = ServiceProtection()
        security_manager = SecurityManager()
        
        print("✅ Все объекты security создаются")
        
        # Проверяем базовые методы
        assert validator.validate_group("1 2 3 4") == True
        assert validator.validate_group("invalid") == False
        
        status = service_protection.get_protection_status()
        assert 'service_active' in status
        
        print("✅ Базовые методы security работают")
        return True
        
    except Exception as e:
        print(f"❌ Ошибка security: {e}")
        return False

def test_web_imports():
    """Тест импортов веб-компонентов"""
    print("\n🔍 ТЕСТ ИМПОРТОВ WEB...")
    
    try:
        from web.components.ml_adapter import MLSystemAdapter
        print("✅ ML адаптер импортируется")
        
        from ml.utils.data_utils import load_dataset, save_dataset
        print("✅ Утилиты данных импортируются")
        
        return True
        
    except Exception as e:
        print(f"❌ Ошибка веб-импортов: {e}")
        return False

def main():
    """Главный тест"""
    print("🎯 ТЕСТ ИСПРАВЛЕНИЯ SECURITY.PY")
    print("=" * 50)
    
    if test_security_imports() and test_web_imports():
        print("\n🎉 SECURITY.PY ИСПРАВЛЕН! Все импорты работают.")
        return 0
    else:
        print("\n⚠️  Есть проблемы с security.py")
        return 1

if __name__ == "__main__":
    exit(main())
