# web/components/sidebar.py
import streamlit as st

def show_sidebar():
    """Показывает боковую панель и возвращает выбранную опцию"""
    st.sidebar.title("Навигация")
    menu_option = st.sidebar.selectbox(
        "Выберите действие:",
        ["Статус системы", "Обучение модели", "Прогнозы", "Добавить данные"]
    )
    return menu_option