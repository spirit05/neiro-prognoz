# web/app.py
import streamlit as st
import sys
import os

# Добавляем пути для импорта
PROJECT_ROOT = '/home/spirit/Desktop/project'
sys.path.insert(0, PROJECT_ROOT)
sys.path.insert(0, os.path.join(PROJECT_ROOT, 'web'))
sys.path.insert(0, os.path.join(PROJECT_ROOT, 'ml'))

from config.paths import DATASET, MODEL
from web.components.sidebar import show_sidebar
from web.components.status import show_system_status
from web.components.training import show_training_interface
from web.components.predictions import show_predictions_interface
from web.components.data import show_data_interface
from web.utils.session import init_session_state, get_system

def main():
    """Основная функция веб-интерфейса"""
    st.set_page_config(
        page_title="AI Prediction System", 
        layout="wide",
        page_icon="🎯"
    )
    st.title("🎯 AI Prediction System")
    
    # Инициализация состояния сессии
    init_session_state()
    
    # Боковая панель
    menu_option = show_sidebar()
    
    # Основной контент
    try:
        if menu_option == "Статус системы":
            show_system_status()
        elif menu_option == "Обучение модели":
            show_training_interface()
        elif menu_option == "Прогнозы":
            show_predictions_interface()
        elif menu_option == "Добавить данные":
            show_data_interface()
    except Exception as e:
        st.error(f"❌ Ошибка в разделе '{menu_option}': {e}")
        st.info("🔄 Попробуйте обновить страницу или перезапустить приложение")

if __name__ == "__main__":
    main()