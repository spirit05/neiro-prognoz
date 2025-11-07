# /opt/dev/web/app.py
import streamlit as st
from components.sidebar import render_sidebar
from components.dashboard import render_dashboard
from components.training_interface import render_training
from components.predictions_view import render_predictions
from components.system_status import render_system_status

def main():
    # Конфигурация страницы
    st.set_page_config(
        page_title="AI Prediction System",
        page_icon="🎯",
        layout="wide",
        initial_sidebar_state="expanded"
    )
    
    # Загрузка кастомных стилей
    with open('web/assets/style.css') as f:
        st.markdown(f'<style>{f.read()}</style>', unsafe_allow_html=True)
    
    # Боковая панель навигации
    current_page = render_sidebar()
    
    # Основной контент
    if current_page == "dashboard":
        render_dashboard()
    elif current_page == "training":
        render_training()
    elif current_page == "predictions":
        render_predictions()
    elif current_page == "system":
        render_system_status()

if __name__ == "__main__":
    main()