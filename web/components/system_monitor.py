# [file name]: web/components/system_monitor.py
"""
Мониторинг системы и аналитика
"""

import streamlit as st
import plotly.graph_objects as go
import plotly.express as px
from web.core.state_manager import StateManager
from ml.data.providers.dataset_manager import DatasetManager
from ml.data.providers.predictions_manager import PredictionsManager


class SystemMonitor:
    """Компонент мониторинга системы"""
    
    @staticmethod
    def render():
        """Рендеринг интерфейса мониторинга"""
        st.header("📈 Мониторинг системы и аналитика")
        
        system = StateManager.get_ml_system()
        if system is None:
            st.error("❌ Система не инициализирована")
            return
        
        # Получаем статус системы
        status = system.get_system_status()
        
        # Верхние метрики системы
        SystemMonitor._render_system_metrics(status)
        
        # Детальная аналитика
        tab1, tab2, tab3 = st.tabs(["📊 Аналитика данных", "🧠 Модели", "📈 Производительность"])
        
        with tab1:
            SystemMonitor._render_data_analytics(status)
        
        with tab2:
            SystemMonitor._render_model_analytics(status)
        
        with tab3:
            SystemMonitor._render_performance_analytics(status)
    
    @staticmethod
    def _render_system_metrics(status):
        """Рендеринг системных метрик"""
        st.subheader("📊 Обзор системы")
        
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            dataset_size = status.get('dataset_size', 0)
            st.metric("📁 Групп данных", dataset_size)
            
            # Индикатор достаточности данных
            if dataset_size >= 100:
                st.success("✅ Данных достаточно")
            elif dataset_size >= 50:
                st.warning("⚠️ Данных маловато")
            else:
                st.error("❌ Данных очень мало")
        
        with col2:
            is_trained = status.get('is_trained', False)
            st.metric("🧠 Статус модели", "Обучена" if is_trained else "Не обучена")
            
            if is_trained:
                st.success("✅ Готова к работе")
            else:
                st.error("❌ Требуется обучение")
        
        with col3:
            system_overview = status.get('system_overview', {})
            system_status = system_overview.get('system_status', 'unknown')
            status_display = {
                'operational': '✅ Работает',
                'error': '❌ Ошибка', 
                'unknown': '⚠️ Неизвестно'
            }.get(system_status, system_status)
            
            st.metric("🔧 Статус системы", status_display)
        
        with col4:
            learning_analytics = status.get('learning_analytics', {})
            recent_accuracy = learning_analytics.get('recent_accuracy', 0)
            st.metric("🎯 Точность", f"{recent_accuracy:.1%}" if recent_accuracy > 0 else "N/A")
    
    @staticmethod
    def _render_data_analytics(status):
        """Рендеринг аналитики данных"""
        st.subheader("📊 Аналитика данных")
        
        try:
            # 🔧 ИСПРАВЛЕНИЕ: Используем DatasetManager и PredictionsManager
            dataset_manager = DatasetManager()
            dataset = dataset_manager.load_dataset()
            
            predictions_manager = PredictionsManager()
            predictions = predictions_manager.load_predictions()
            
            col1, col2 = st.columns(2)
            
            with col1:
                # Статистика датасета
                st.info("**Статистика датасета:**")
                st.write(f"• Всего групп: {len(dataset)}")
                
                if dataset:
                    # Анализ распределения чисел
                    all_numbers = []
                    for group_str in dataset:
                        numbers = [int(x) for x in group_str.split()]
                        all_numbers.extend(numbers)
                    
                    st.write(f"• Всего чисел: {len(all_numbers)}")
                    st.write(f"• Уникальных чисел: {len(set(all_numbers))}")
                    st.write(f"• Среднее значение: {sum(all_numbers) / len(all_numbers):.1f}")
            
            with col2:
                # Статистика прогнозов
                st.info("**Статистика прогнозов:**")
                if predictions:
                    st.write(f"• Всего прогнозов: {len(predictions)}")
                    
                    # Анализ уверенности
                    confidences = [score for _, score in predictions]
                    if confidences:
                        avg_confidence = sum(confidences) / len(confidences)
                        max_confidence = max(confidences)
                        min_confidence = min(confidences)
                        
                        st.write(f"• Средняя уверенность: {avg_confidence:.4f}")
                        st.write(f"• Макс. уверенность: {max_confidence:.4f}")
                        st.write(f"• Мин. уверенность: {min_confidence:.4f}")
                else:
                    st.write("• Прогнозы не сгенерированы")
            
            # Визуализация распределения чисел
            if dataset:
                st.subheader("📈 Распределение чисел в датасете")
                
                all_numbers = []
                for group_str in dataset:
                    numbers = [int(x) for x in group_str.split()]
                    all_numbers.extend(numbers)
                
                # Создаем гистограмму
                fig = px.histogram(
                    x=all_numbers,
                    nbins=26,
                    title="Частота появления чисел",
                    labels={'x': 'Число', 'y': 'Частота'}
                )
                st.plotly_chart(fig, use_container_width=True)
                
        except Exception as e:
            st.error(f"❌ Ошибка анализа данных: {e}")
    
    @staticmethod
    def _render_model_analytics(status):
        """Рендеринг аналитики моделей"""
        st.subheader("🧠 Аналитика моделей")
        
        system_overview = status.get('system_overview', {})
        model_metrics = system_overview.get('model_metrics', {})
        
        if model_metrics:
            st.success(f"✅ В системе {len(model_metrics)} моделей")
            
            for model_id, metrics in model_metrics.items():
                with st.expander(f"Модель: {model_id}", expanded=False):
                    col1, col2 = st.columns(2)
                    
                    with col1:
                        st.write("**Основные метрики:**")
                        st.write(f"• Статус: {metrics.get('status', 'unknown')}")
                        st.write(f"• Количество фич: {metrics.get('feature_count', 0)}")
                        
                        if 'metadata' in metrics:
                            metadata = metrics['metadata']
                            st.write(f"• Тип: {metadata.get('model_type', 'unknown')}")
                            st.write(f"• Версия: {metadata.get('version', 'unknown')}")
                    
                    with col2:
                        st.write("**Производительность:**")
                        performance = metrics.get('metadata', {}).get('performance_metrics', {})
                        if performance:
                            for metric, value in list(performance.items())[:3]:  # Показываем первые 3 метрики
                                st.write(f"• {metric}: {value:.4f}")
        else:
            st.warning("⚠️ Информация о моделях недоступна")
        
        # Аналитика обучения
        learning_analytics = status.get('learning_analytics', {})
        if learning_analytics and 'learning_curves' in learning_analytics:
            st.subheader("📊 Кривые обучения")
            
            curves = learning_analytics['learning_curves']
            if curves and 'training_loss' in curves and 'validation_loss' in curves:
                fig = go.Figure()
                
                fig.add_trace(go.Scatter(
                    y=curves['training_loss'],
                    mode='lines',
                    name='Training Loss',
                    line=dict(color='blue')
                ))
                
                fig.add_trace(go.Scatter(
                    y=curves['validation_loss'],
                    mode='lines', 
                    name='Validation Loss',
                    line=dict(color='red')
                ))
                
                fig.update_layout(
                    title='Кривые обучения',
                    xaxis_title='Эпоха',
                    yaxis_title='Loss',
                    showlegend=True
                )
                
                st.plotly_chart(fig, use_container_width=True)
    
    @staticmethod
    def _render_performance_analytics(status):
        """Рендеринг аналитики производительности"""
        st.subheader("📈 Аналитика производительности")
        
        system_overview = status.get('system_overview', {})
        performance_metrics = system_overview.get('performance_metrics', {})
        learning_analytics = status.get('learning_analytics', {})
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.info("**Общая производительность:**")
            
            if performance_metrics:
                st.write(f"• Всего прогнозов: {performance_metrics.get('total_predictions', 0)}")
                st.write(f"• Сессий обучения: {performance_metrics.get('total_training_sessions', 0)}")
                st.write(f"• Моделей в системе: {performance_metrics.get('models_registered', 0)}")
            else:
                st.write("• Метрики производительности недоступны")
        
        with col2:
            st.info("**Аналитика обучения:**")
            
            if learning_analytics:
                st.write(f"• Всего сессий: {learning_analytics.get('total_training_sessions', 0)}")
                st.write(f"• Лучшая точность: {learning_analytics.get('best_accuracy', 0):.1%}")
                st.write(f"• Среднее время: {learning_analytics.get('average_training_time', 0):.1f}с")
            else:
                st.write("• Аналитика обучения недоступна")
        
        # Тренд точности
        if learning_analytics and 'prediction_accuracy_trend' in learning_analytics:
            accuracy_trend = learning_analytics['prediction_accuracy_trend']
            if accuracy_trend:
                st.subheader("📊 Тренд точности прогнозов")
                
                fig = go.Figure()
                fig.add_trace(go.Scatter(
                    y=accuracy_trend,
                    mode='lines+markers',
                    name='Точность',
                    line=dict(color='green')
                ))
                
                fig.update_layout(
                    title='История точности прогнозов',
                    xaxis_title='Сессия',
                    yaxis_title='Точность',
                    yaxis_tickformat='.1%'
                )
                
                st.plotly_chart(fig, use_container_width=True)
        
        # Важность фич
        if learning_analytics and 'feature_importance' in learning_analytics:
            feature_importance = learning_analytics['feature_importance']
            if feature_importance:
                st.subheader("🔍 Важность фич")
                
                features = list(feature_importance.keys())
                importance = list(feature_importance.values())
                
                fig = px.bar(
                    x=importance,
                    y=features,
                    orientation='h',
                    title='Важность фич',
                    labels={'x': 'Важность', 'y': 'Фича'}
                )
                
                st.plotly_chart(fig, use_container_width=True)
