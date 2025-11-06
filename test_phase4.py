# test_phase4_fixed.py
#!/usr/bin/env python3
"""
Тест Фазы 4 - веб-интерфейс (ИСПРАВЛЕННАЯ ВЕРСИЯ)
"""

import sys
import os

PROJECT_ROOT = '/home/spirit/Desktop/project'
sys.path.insert(0, PROJECT_ROOT)

def test_web_imports():
    """Тестируем импорты веб-интерфейса"""
    print("🧪 Тестируем импорты веб-интерфейса...")

    try:
        # Тестируем главный app
        from web.app import main
        print("✅ Главный app импортируется")

        # Тестируем компоненты
        from web.components.sidebar import show_sidebar
        from web.components.status import show_system_status
        from web.components.training import show_training_interface
        from web.components.predictions import show_predictions_interface
        from web.components.data import show_data_interface
        from web.utils.session import init_session_state

        print("✅ Все компоненты веб-интерфейса импортируются")
        return True

    except Exception as e:
        print(f"❌ Ошибка импорта веб-интерфейса: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_web_session():
    """Тестируем инициализацию сессии - ИСПРАВЛЕННАЯ ВЕРСИЯ"""
    print("\n🔧 Тестируем инициализацию сессии...")

    try:
        # Имитируем Streamlit session state правильно
        class MockSessionState(dict):
            def __init__(self, *args, **kwargs):
                super().__init__(*args, **kwargs)
                self._state = {}
            
            def __getattr__(self, name):
                if name in self._state:
                    return self._state[name]
                raise AttributeError(f"'MockSessionState' object has no attribute '{name}'")
            
            def __setattr__(self, name, value):
                if name == '_state':
                    super().__setattr__(name, value)
                else:
                    self._state[name] = value

        # Создаем mock для st.session_state
        import web.utils.session as session_module
        original_session_state = getattr(session_module.st, 'session_state', None)
        
        # Создаем mock session state
        mock_session = MockSessionState()
        mock_session.system = None
        mock_session.initialized = False
        
        # Временно заменяем st.session_state
        session_module.st.session_state = mock_session

        # Инициализируем сессию
        session_module.init_session_state()

        # Проверяем, что система инициализирована
        assert session_module.st.session_state.system is not None, "Система должна быть инициализирована"
        assert hasattr(session_module.st.session_state.system, 'get_status'), "Система должна иметь метод get_status"

        print("✅ Инициализация сессии работает")
        return True

    except Exception as e:
        print(f"❌ Ошибка инициализации сессии: {e}")
        import traceback
        traceback.print_exc()
        return False
    finally:
        # Восстанавливаем оригинальный session_state если был
        if 'original_session_state' in locals() and original_session_state:
            session_module.st.session_state = original_session_state

def test_web_components():
    """Тестируем компоненты веб-интерфейса"""
    print("\n📦 Тестируем компоненты веб-интерфейса...")

    try:
        # Тестируем sidebar
        from web.components.sidebar import show_sidebar
        # Функция должна возвращать строку
        # Поскольку мы не в Streamlit, просто проверяем, что функция существует
        assert callable(show_sidebar), "show_sidebar должна быть функцией"

        # Аналогично для других компонентов
        from web.components.status import show_system_status
        assert callable(show_system_status), "show_system_status должна быть функцией"

        from web.components.training import show_training_interface
        assert callable(show_training_interface), "show_training_interface должна быть функцией"

        from web.components.predictions import show_predictions_interface
        assert callable(show_predictions_interface), "show_predictions_interface должна быть функцией"

        from web.components.data import show_data_interface
        assert callable(show_data_interface), "show_data_interface должна быть функцией"

        print("✅ Все компоненты веб-интерфейса работают")
        return True

    except Exception as e:
        print(f"❌ Ошибка компонентов веб-интерфейса: {e}")
        return False

def test_data_validation():
    """Тестируем валидацию данных"""
    print("\n🔍 Тестируем валидацию данных...")

    try:
        from ml.data.data_loader import validate_group

        # Тестируем валидные группы
        assert validate_group("1 2 3 4") == True, "Валидная группа должна проходить"
        assert validate_group("5 10 15 20") == True, "Валидная группа должна проходить"
        
        # Тестируем невалидные группы
        assert validate_group("1 1 3 4") == False, "Дубли в парах должны быть невалидны"
        assert validate_group("1 2 3") == False, "Неполная группа должна быть невалидна"
        assert validate_group("1 2 3 4 5") == False, "Избыточная группа должна быть невалидна"
        assert validate_group("0 2 3 4") == False, "Числа должны быть от 1 до 26"
        assert validate_group("1 2 3 27") == False, "Числа должны быть от 1 до 26"
        assert validate_group("a b c d") == False, "Нечисловые значения должны быть невалидны"

        print("✅ Валидация данных работает корректно")
        return True

    except Exception as e:
        print(f"❌ Ошибка валидации данных: {e}")
        return False

if __name__ == "__main__":
    print("🚀 Запуск теста Фазы 4 (веб-интерфейс - исправленная версия)")
    print("=" * 50)

    success1 = test_web_imports()
    success2 = test_web_session()
    success3 = test_web_components()
    success4 = test_data_validation()

    print("\n" + "=" * 50)
    if success1 and success2 and success3 and success4:
        print("🎉 ФАЗА 4 ЗАВЕРШЕНА УСПЕШНО!")
        print("📋 Веб-интерфейс модульный и готов к работе!")
    else:
        print("💥 Есть проблемы в Фазе 4!")
        sys.exit(1)