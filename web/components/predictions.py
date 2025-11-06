# web/components/predictions.py
import streamlit as st

def show_predictions_interface():
    """Интерфейс прогнозов"""
    st.header("🔮 Прогнозы")
    
    top_k = st.slider("Количество прогнозов", min_value=1, max_value=20, value=10)
    
    if st.button("Сгенерировать прогнозы"):
        with st.spinner("Генерация прогнозов..."):
            predictions = st.session_state.system.predict(top_k=top_k)
            
        if predictions:
            st.success(f"Сгенерировано {len(predictions)} прогнозов")
            for i, (group, score) in enumerate(predictions, 1):
                st.write(f"{i}. {group} (вероятность: {score:.3%})")
        else:
            st.error("Не удалось сгенерировать прогнозы")