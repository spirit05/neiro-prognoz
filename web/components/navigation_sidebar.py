# [file name]: web/components/navigation_sidebar.py
"""
Боковая панель навигации
"""

import streamlit as st
from web.core.state_manager import StateManager
from ml.data.providers.dataset_manager import DatasetManager


class NavigationSidebar:
    """Компонент боковой панели навигации"""
    
    @staticmethod
    def render():
        """Рендеринг боковой панели"""
        with st.sidebar:
            st.header("🧭 Навигация")
            
            # Выбор представления
            view_options = {
                'dashboard': '📊 Обзор системы',
                'training': '🧠 Обучение модели', 
                'prediction': '🔮 Получить прогнозы',
                'add_group': '➕ Добавить группы',
                'monitor': '📈 Мониторинг'
            }
            
            current_view = st.selectbox(
                "Выберите раздел:",
                options=list(view_options.keys()),
                format_func=lambda x: view_options[x],
                key='view_selector'
            )
            
            # Обновляем текущее представление
            StateManager.set_current_view(current_view)
            
            st.markdown("---")
            NavigationSidebar._render_system_status()
            
            return current_view
    
    @staticmethod
    def _render_system_status():
        """Рендеринг статуса системы"""
        st.header("📊 Статус системы")
        
        system = StateManager.get_ml_system()
        if system is None:
            st.error("❌ Система не инициализирована")
            return
        
        try:
            status = system.get_system_status()
            
            # Архитектура
            st.success("✅ МОДУЛЬНАЯ АРХИТЕКТУРА")
            st.info(f"🏗️ {status.get('architecture', 'WorkflowManager')}")
            
            # Статус обучения
            if status.get('is_trained', False):
                st.success("✅ Модель обучена")
            else:
                st.warning("⚠️ Модель не обучена")
            
            # Данные
            dataset_size = status.get('dataset_size', 0)
            st.info(f"📁 Групп в датасете: {dataset_size}")
            
            if status.get('has_sufficient_data', False):
                st.success("✅ Данных достаточно")
            else:
                st.warning(f"⚠️ Нужно больше данных (минимум 50)")
            
            # Последняя группа
            try:
                # 🔧 ИСПРАВЛЕНИЕ: Используем DatasetManager вместо data_utils
                dataset_manager = DatasetManager()
                dataset = dataset_manager.load_dataset()
                if dataset:
                    last_group = dataset[-1] if dataset else "нет данных"
                    st.info(f"📋 Последняя группа: {last_group}")
            except Exception as e:
                st.info("📋 Последняя группа: не удалось загрузить")
                
        except Exception as e:
            st.error(f"❌ Ошибка получения статуса: {e}")
