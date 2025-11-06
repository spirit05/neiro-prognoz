# web/components/status.py
import streamlit as st

def show_system_status():
    """Показать статус системы"""
    st.header("📊 Статус системы")
    
    status = st.session_state.system.get_status()
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.metric("Модель обучена", "✅" if status['is_trained'] else "❌")
        st.metric("Размер датасета", status['dataset_size'])
        
    with col2:
        st.metric("Тип модели", status['model_type'])
        if status.get('learning_stats'):
            accuracy = status['learning_stats'].get('recent_accuracy_avg', 0)
            st.metric("Средняя точность", f"{accuracy:.1%}")

    # Дополнительная информация
    with st.expander("Подробная информация"):
        st.json(status)