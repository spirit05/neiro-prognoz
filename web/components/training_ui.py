# [file name]: web/components/training_ui.py
"""
Интерфейс обучения модели
"""

import streamlit as st
from ml.utils.data_utils import save_predictions

def show_training_ui(system, run_operation_sync):
    """Показать интерфейс обучения"""
    st.header("🧠 Обучение модели AI")
    
    col1, col2 = st.columns([2, 1])
    
    with col1:
        st.info("""
        **Полное обучение модели на всех данных:**
        - Анализ 9000+ групп чисел
        - Создание ансамблевой системы
        - Генерация первых прогнозов
        - **Время: 15-20 минут**
        """)
    
    with col2:
        st.warning("""
        **⚠️ Внимание:**
        Не закрывайте страницу во время обучения!
        """)
    
    # Кнопка обучения
    if st.button("🚀 Начать полное обучение", type="primary"):
        if not system:
            st.error("❌ Система не инициализирована")
            return
            
        # Запускаем операцию СИНХРОННО
        with st.spinner("🔄 Запуск обучения..."):
            result = run_operation_sync("training")
        
        # Показываем результат
        if hasattr(st.session_state, 'operation_error') and st.session_state.operation_error:
            st.error(f"❌ Ошибка обучения: {st.session_state.operation_error}")
        elif hasattr(st.session_state, 'operation_result') and st.session_state.operation_result:
            st.balloons()
            st.success("🎉 Обучение успешно завершено!")
            
            st.subheader("🎯 Первые прогнозы после обучения")
            for i, (group, score) in enumerate(st.session_state.operation_result[:4], 1):
                confidence = "🟢 ВЫСОКАЯ" if score > 0.01 else "🟡 СРЕДНЯЯ" if score > 0.001 else "🔴 НИЗКАЯ"
                st.write(f"**{i}.** `{group[0]} {group[1]} {group[2]} {group[3]}`")
                st.write(f"   Уверенность: `{score:.6f}` {confidence}")
            
            # Сохраняем прогнозы
            try:
                save_predictions(st.session_state.operation_result)
                st.info("💾 Прогнозы сохранены в кэш")
            except Exception as e:
                st.warning(f"⚠️ Не удалось сохранить прогнозы: {e}")
        else:
            st.warning("⚠️ Обучение завершено, но прогнозы не получены")