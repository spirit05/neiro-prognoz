# web/utils/session.py
import streamlit as st
from ml.core.system import SimpleNeuralSystem

def init_session_state():
    """Инициализация состояния сессии - УЛУЧШЕННАЯ ВЕРСИЯ"""
    try:
        # Используем безопасную проверку наличия ключей
        if not hasattr(st.session_state, 'system') or st.session_state.system is None:
            st.session_state.system = SimpleNeuralSystem()
            st.success("✅ Система инициализирована")
        
        if not hasattr(st.session_state, 'initialized'):
            st.session_state.initialized = False
            
    except Exception as e:
        st.error(f"❌ Ошибка инициализации сессии: {e}")

def get_system():
    """Безопасное получение системы из сессии"""
    init_session_state()  # Гарантируем инициализацию
    return st.session_state.system

def is_initialized():
    """Проверка инициализации системы"""
    return hasattr(st.session_state, 'initialized') and st.session_state.initialized

def set_initialized(value=True):
    """Установка статуса инициализации"""
    st.session_state.initialized = value