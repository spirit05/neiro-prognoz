# [file name]: web/app.py
#!/usr/bin/env python3
"""
Главное приложение Streamlit для ML системы с WorkflowManager
"""

import os
import sys
import logging
import streamlit as st

# Добавляем корневую директорию проекта в путь
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, project_root)

from web.core.ml_integration import MLIntegration
from web.core.state_manager import StateManager
from web.components import (
    NavigationSidebar,
    DataDashboard,
    TrainingControl,
    PredictionInterface,
    GroupAddition,
    SystemMonitor,
    apply_custom_styles
)

# Настройка логирования
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger('MLWebInterface')

def initialize_system():
    """Инициализация ML системы"""
    if StateManager.get_ml_system() is not None:
        return True
    
    try:
        with st.spinner("🔄 Инициализация ML системы с WorkflowManager..."):
            system = MLIntegration()
            if system.initialize():
                StateManager.set_ml_system(system)
                StateManager.add_progress_message("✅ ML система успешно инициализирована")
                return True
            else:
                st.error("❌ Не удалось инициализировать ML систему")
                return False
    except Exception as e:
        st.error(f"❌ Ошибка инициализации: {e}")
        logger.exception("Ошибка инициализации системы")
        return False

def main():
    """Главная функция приложения"""
    
    # Настройка страницы
    st.set_page_config(
        page_title="AI Прогноз Последовательностей - WorkflowManager",
        page_icon="🔢",
        layout="wide",
        initial_sidebar_state="expanded"
    )
    
    # Применяем кастомные стили
    apply_custom_styles()
    
    # Инициализация состояния
    StateManager.initialize()
    
    # Заголовок приложения
    st.markdown(
        '<h1 class="main-header">🔢 AI Прогноз Числовых Последовательностей</h1>',
        unsafe_allow_html=True
    )
    st.markdown(
        '<h3 class="sub-header">МОДУЛЬНАЯ АРХИТЕКТУРА С WORKFLOWMANAGER</h3>', 
        unsafe_allow_html=True
    )
    
    # Инициализация системы
    if not initialize_system():
        st.error("""
        ❌ Не удалось инициализировать систему. Возможные причины:
        - Отсутствуют конфигурационные файлы
        - Проблемы с зависимостями
        - Ошибки в настройках ML системы
        """)
        return
    
    # Боковая панель навигации
    current_view = NavigationSidebar.render()
    
    # Основное содержимое в зависимости от выбранного представления
    try:
        if current_view == 'dashboard':
            DataDashboard.render()
        elif current_view == 'training':
            TrainingControl.render()
        elif current_view == 'prediction':
            PredictionInterface.render()
        elif current_view == 'add_group':
            GroupAddition.render()
        elif current_view == 'monitor':
            SystemMonitor.render()
        else:
            st.error(f"Неизвестное представление: {current_view}")
    except Exception as e:
        logger.error(f"Ошибка в рендеринге компонента {current_view}: {e}")
        st.error(f"❌ Ошибка отображения интерфейса: {e}")

if __name__ == "__main__":
    main()
