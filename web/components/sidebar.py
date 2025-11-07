# [file name]: web/components/sidebar.py
"""
Боковая панель навигации
"""

import streamlit as st
from ml.utils.data_utils import load_dataset

def show_sidebar(system):
    """Показать боковую панель"""
    st.sidebar.header("📊 Статус системы")
    
    if system and hasattr(system, 'get_status'):
        try:
            status = system.get_status()
            
            # Архитектура
            st.sidebar.success("✅ МОДУЛЬНАЯ АРХИТЕКТУРА")
            
            # Статус обучения
            if status['is_trained']:
                st.sidebar.success("✅ Модель обучена")
            else:
                st.sidebar.warning("⚠️ Модель не обучена")
            
            # Данные
            st.sidebar.info(f"📁 Групп в датасете: {status['dataset_size']}")
            
            if status['has_sufficient_data']:
                st.sidebar.success("✅ Данных достаточно")
            else:
                st.sidebar.warning(f"⚠️ Нужно больше данных")
            
            # Последняя группа
            try:
                dataset = load_dataset()
                if dataset:
                    last_group = dataset[-1]
                    st.sidebar.info(f"📋 Последняя группа: {last_group}")
            except:
                pass
                
        except Exception as e:
            st.sidebar.error(f"Ошибка статуса: {e}")
    else:
        st.sidebar.error("❌ Система не инициализирована")