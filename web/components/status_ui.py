# [file name]: web/components/status_ui.py
"""
Интерфейс статуса и аналитики
"""

import streamlit as st
from ml.utils.data_utils import load_predictions, load_dataset

def show_status_ui(system):
    """Показать интерфейс статуса и аналитики"""
    st.header("📊 Обзор данных и аналитика")
    
    if not system:
        st.error("❌ Система не инициализирована")
        return
    
    try:
        # Статус системы
        status = system.get_status()
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.subheader("🧠 Статус модели")
            if status['is_trained']:
                st.success("✅ Модель обучена")
            else:
                st.warning("⚠️ Модель не обучена")
            
            st.info(f"📁 Групп в датасете: {status['dataset_size']}")
            
            if status['has_sufficient_data']:
                st.success("✅ Данных достаточно")
            else:
                st.warning(f"⚠️ Нужно больше данных (минимум 50)")
        
        with col2:
            st.subheader("🔧 Система")
            st.info(f"🎯 Архитектура: {status.get('architecture', 'МОДУЛЬНАЯ')}")
            st.info(f"🏗️ Тип: {status.get('model_type', 'УСИЛЕННАЯ НЕЙРОСЕТЬ')}")
        
        # Последние прогнозы
        st.subheader("🎯 Последние прогнозы")
        predictions = load_predictions()
        if predictions:
            for i, (group, score) in enumerate(predictions[:4], 1):
                confidence = "🟢 ВЫСОКАЯ" if score > 0.01 else "🟡 СРЕДНЯЯ" if score > 0.001 else "🔴 НИЗКАЯ"
                st.write(f"**{i}.** `{group[0]} {group[1]} {group[2]} {group[3]}` - уверенность: `{score:.6f}` {confidence}")
        else:
            st.info("📝 Прогнозы еще не сгенерированы")
        
        # Аналитика самообучения
        st.subheader("📈 Аналитика самообучения")
        learning_stats = system.get_learning_insights()
        
        if 'message' in learning_stats:
            st.info(learning_stats['message'])
        else:
            col1, col2 = st.columns(2)
            with col1:
                if 'recent_accuracy_avg' in learning_stats:
                    accuracy = learning_stats['recent_accuracy_avg']
                    st.metric("🎯 Средняя точность", f"{accuracy:.1%}")
                if 'total_predictions_analyzed' in learning_stats:
                    st.metric("📊 Проанализировано прогнозов", learning_stats['total_predictions_analyzed'])
            
            with col2:
                if 'best_accuracy' in learning_stats:
                    best = learning_stats['best_accuracy']
                    st.metric("🏆 Лучшая точность", f"{best:.1%}")
                if 'worst_accuracy' in learning_stats:
                    worst = learning_stats['worst_accuracy']
                    st.metric("📉 Худшая точность", f"{worst:.1%}")
            
            # Рекомендации
            if 'recommendations' in learning_stats and learning_stats['recommendations']:
                st.subheader("💡 Рекомендации")
                for rec in learning_stats['recommendations']:
                    st.write(f"• {rec}")
        
    except Exception as e:
        st.error(f"❌ Ошибка загрузки данных: {e}")