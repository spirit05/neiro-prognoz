# [file name]: web/core/state_manager.py
"""
Управление состоянием веб-интерфейса
"""

import streamlit as st
from typing import Dict, Any, List, Optional
from datetime import datetime


class StateManager:
    """Менеджер состояния веб-интерфейса"""
    
    @staticmethod
    def initialize():
        """Инициализация состояния сессии"""
        if 'ml_system' not in st.session_state:
            st.session_state.ml_system = None
        
        if 'operation_in_progress' not in st.session_state:
            st.session_state.operation_in_progress = False
            
        if 'last_operation_result' not in st.session_state:
            st.session_state.last_operation_result = None
            
        if 'last_operation_error' not in st.session_state:
            st.session_state.last_operation_error = None
            
        if 'progress_messages' not in st.session_state:
            st.session_state.progress_messages = []
            
        if 'current_view' not in st.session_state:
            st.session_state.current_view = 'dashboard'
    
    @staticmethod
    def set_ml_system(system):
        """Установка ML системы"""
        st.session_state.ml_system = system
    
    @staticmethod
    def get_ml_system():
        """Получение ML системы"""
        return st.session_state.ml_system
    
    @staticmethod
    def set_operation_in_progress(status: bool):
        """Установка статуса операции"""
        st.session_state.operation_in_progress = status
    
    @staticmethod
    def is_operation_in_progress() -> bool:
        """Проверка выполнения операции"""
        return st.session_state.operation_in_progress
    
    @staticmethod
    def set_operation_result(result):
        """Установка результата операции"""
        st.session_state.last_operation_result = result
        st.session_state.last_operation_error = None
    
    @staticmethod
    def set_operation_error(error: str):
        """Установка ошибки операции"""
        st.session_state.last_operation_error = error
        st.session_state.last_operation_result = None
    
    @staticmethod
    def get_operation_result():
        """Получение результата операции"""
        return st.session_state.last_operation_result
    
    @staticmethod
    def get_operation_error():
        """Получение ошибки операции"""
        return st.session_state.last_operation_error
    
    @staticmethod
    def add_progress_message(message: str):
        """Добавление сообщения прогресса"""
        timestamp = datetime.now().strftime('%H:%M:%S')
        formatted_message = f"{timestamp} - {message}"
        st.session_state.progress_messages.append(formatted_message)
        # Ограничиваем количество сообщений
        if len(st.session_state.progress_messages) > 50:
            st.session_state.progress_messages = st.session_state.progress_messages[-50:]
    
    @staticmethod
    def get_progress_messages() -> List[str]:
        """Получение сообщений прогресса"""
        return st.session_state.progress_messages
    
    @staticmethod
    def clear_progress_messages():
        """Очистка сообщений прогресса"""
        st.session_state.progress_messages = []
    
    @staticmethod
    def set_current_view(view: str):
        """Установка текущего представления"""
        st.session_state.current_view = view
    
    @staticmethod
    def get_current_view() -> str:
        """Получение текущего представления"""
        return st.session_state.current_view
