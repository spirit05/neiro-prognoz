# [file name]: web/components/data_dashboard.py
"""
Главная панель - обзор данных и аналитика
"""

import streamlit as st
from web.core.state_manager import StateManager
from ml.data.providers.dataset_manager import DatasetManager
from ml.data.providers.predictions_manager import PredictionsManager


class DataDashboard:
    """Компонент главной панели данных"""
    
    @staticmethod
    def render():
        """Рендеринг главной панели"""
        st.header("📊 Обзор системы и аналитика")
        
        system = StateManager.get_ml_system()
        if system is None:
            st.error("❌ Система не инициализирована")
            return
        
        # Получаем статус системы
        status = system.get_system_status()
        
        # Верхние метрики
        DataDashboard._render_system_metrics(status)
        
        # Колонки с детальной информацией
        col1, col2 = st.columns(2)
        
        with col1:
            DataDashboard._render_model_status(status)
        
        with col2:
            DataDashboard._render_data_status(status)
        
        # Последние прогнозы
        DataDashboard._render_recent_predictions()
        
        # Аналитика обучения
        DataDashboard._render_learning_analytics(status)
    
    @staticmethod
    def _render_system_metrics(status):
        """Рендеринг системных метрик"""
        st.subheader("📈 Ключевые метрики")
        
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            dataset_size = status.get('dataset_size', 0)
            st.metric("📁 Групп данных", dataset_size)
        
        with col2:
            is_trained = status.get('is_trained', False)
            status_text = "Обучена" if is_trained else "Не обучена"
            st.metric("🧠 Статус модели", status_text)
        
        with col3:
            has_sufficient_data = status.get('has_sufficient_data', False)
            data_status = "Достаточно" if has_sufficient_data else "Недостаточно"
            st.metric("📊 Данные", data_status)
        
        with col4:
            architecture = status.get('architecture', 'WorkflowManager')
            st.metric("🏗️ Архитектура", architecture)
    
    @staticmethod
    def _render_model_status(status):
        """Рендеринг статуса модели"""
        st.subheader("🧠 Статус модели")
        
        system_overview = status.get('system_overview', {})
        
        if system_overview:
            st.info(f"**Статус системы:** {system_overview.get('system_status', 'unknown')}")
            st.info(f"**Статус модели:** {system_overview.get('model_status', 'unknown')}")
            st.info(f"**Статус обучения:** {system_overview.get('training_status', 'unknown')}")
            
            last_training = system_overview.get('last_training')
            if last_training:
                st.info(f"**Последнее обучение:** {last_training}")
            
            # Рекомендации
            recommendations = system_overview.get('recommendations', [])
            if recommendations:
                st.subheader("💡 Рекомендации")
                for rec in recommendations:
                    st.write(f"• {rec}")
        else:
            st.warning("Информация о системе недоступна")
    
    @staticmethod
    def _render_data_status(status):
        """Рендеринг статуса данных"""
        st.subheader("📁 Статус данных")
        
        system_overview = status.get('system_overview', {})
        
        if system_overview:
            st.info(f"**Всего групп:** {system_overview.get('total_groups', 0)}")
            st.info(f"**Валидных групп:** {system_overview.get('valid_groups', 0)}")
            st.info(f"**Статус данных:** {system_overview.get('data_status', 'unknown')}")
            
            # Производительность
            performance = system_overview.get('performance_metrics', {})
            if performance:
                st.info(f"**Всего прогнозов:** {performance.get('total_predictions', 0)}")
                st.info(f"**Сессий обучения:** {performance.get('total_training_sessions', 0)}")
        else:
            st.warning("Информация о данных недоступна")
        
        # Последние данные
        try:
            # 🔧 ИСПРАВЛЕНИЕ: Используем DatasetManager
            dataset_manager = DatasetManager()
            dataset = dataset_manager.load_dataset()
            if dataset and len(dataset) > 0:
                st.subheader("📋 Последние группы")
                for i, group in enumerate(dataset[-3:][::-1]):
                    st.write(f"**{len(dataset) - i}.** `{group}`")
        except Exception as e:
            st.warning("Не удалось загрузить последние группы")
    
    @staticmethod
    def _render_recent_predictions():
        """Рендеринг последних прогнозов"""
        st.subheader("🎯 Последние прогнозы")
        
        try:
            # 🔧 ИСПРАВЛЕНИЕ: Используем PredictionsManager
            predictions_manager = PredictionsManager()
            predictions = predictions_manager.load_predictions()
            if predictions:
                for i, (group, score) in enumerate(predictions[:5]):
                    confidence = "🟢 ВЫСОКАЯ" if score > 0.01 else "🟡 СРЕДНЯЯ" if score > 0.001 else "🔴 НИЗКАЯ"
                    st.write(f"**{i+1}.** `{group[0]} {group[1]} {group[2]} {group[3]}`")
                    st.write(f"   Уверенность: `{score:.6f}` {confidence}")
            else:
                st.info("📝 Прогнозы еще не сгенерированы")
        except Exception as e:
            st.warning("Не удалось загрузить прогнозы")
    
    @staticmethod
    def _render_learning_analytics(status):
        """Рендеринг аналитики обучения"""
        st.subheader("📈 Аналитика обучения")
        
        learning_analytics = status.get('learning_analytics', {})
        
        if learning_analytics and 'recent_accuracy' in learning_analytics:
            col1, col2, col3, col4 = st.columns(4)
            
            with col1:
                recent_accuracy = learning_analytics.get('recent_accuracy', 0)
                st.metric("🎯 Текущая точность", f"{recent_accuracy:.1%}")
            
            with col2:
                best_accuracy = learning_analytics.get('best_accuracy', 0)
                st.metric("🏆 Лучшая точность", f"{best_accuracy:.1%}")
            
            with col3:
                total_sessions = learning_analytics.get('total_training_sessions', 0)
                st.metric("🔄 Сессии обучения", total_sessions)
            
            with col4:
                avg_time = learning_analytics.get('average_training_time', 0)
                st.metric("⏱️ Ср. время обучения", f"{avg_time:.1f}с")
            
            # Тренд точности
            accuracy_trend = learning_analytics.get('prediction_accuracy_trend', [])
            if accuracy_trend:
                st.line_chart(accuracy_trend)
                st.caption("📊 Тренд точности прогнозов")
        else:
            st.info("Аналитика обучения будет доступна после первого обучения")
