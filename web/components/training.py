# web/components/training.py
import streamlit as st

def show_training_interface():
    """Интерфейс обучения"""
    st.header("🧠 Обучение модели")
    
    epochs = st.number_input("Количество эпох", min_value=1, max_value=100, value=20)
    
    if st.button("Начать обучение", type="primary"):
        with st.spinner("Обучение модели... Это займет 15-20 минут"):
            result = st.session_state.system.train(epochs=epochs)
            
        if result:
            st.success("Обучение завершено успешно!")
        else:
            st.error("Ошибка при обучении модели")