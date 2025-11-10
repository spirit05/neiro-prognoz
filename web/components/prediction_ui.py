# [file name]: web/components/prediction_ui.py
"""
Интерфейс прогнозирования
"""

import streamlit as st
from ml.utils.data_utils import save_predictions
from .utils import show_operation_progress, show_recent_logs

def show_prediction_ui(system, run_operation_sync):
    """Показать интерфейс прогнозирования"""
    st.header("🔮 Получить прогнозы")
    
    st.info("""
    **AI проанализирует паттерны и сгенерирует прогнозы:**
    - Использует обученную модель
    - Применяет ансамблевые методы
    - Учитывает исторические паттерны
    - **Время: 2-5 минут**
    """)
    
    # Кнопка прогнозирования
    if st.button("🎯 Сгенерировать прогнозы", type="primary"):
        if not system:
            st.error("❌ Система не инициализирована")
            return
            
        # Проверяем что модель обучена
        status = system.get_status()
        if not status['is_trained']:
            st.error("❌ Модель не обучена! Сначала выполните обучение.")
            return
        
        # Показываем ожидаемые этапы
        st.subheader("📋 План операции:")
        show_operation_progress("prediction", 0, 5)
        
        # Запускаем операцию СИНХРОННО
        with st.spinner("🔄 Генерация прогнозов..."):
            result = run_operation_sync("prediction")
        
        # Показываем результат
        if hasattr(st.session_state, 'operation_error') and st.session_state.operation_error:
            st.error(f"❌ Ошибка прогнозирования: {st.session_state.operation_error}")
        elif hasattr(st.session_state, 'operation_result') and st.session_state.operation_result:
            st.success(f"✅ Сгенерировано {len(st.session_state.operation_result)} прогнозов")
            
            # Показываем завершенные этапы
            show_operation_progress("prediction", 5, 5, "Прогнозирование завершено!")
            
            # Показываем логи если есть
            if hasattr(st.session_state, 'progress_messages') and st.session_state.progress_messages:
                show_recent_logs(st.session_state.progress_messages, max_logs=5)
            
            st.subheader("🏆 Топ прогнозы")
            cols = st.columns(2)
            
            for i, (group, score) in enumerate(st.session_state.operation_result):
                with cols[i % 2]:
                    confidence = "🟢 ВЫСОКАЯ" if score > 0.01 else "🟡 СРЕДНЯЯ" if score > 0.001 else "🔴 НИЗКАЯ"
                    
                    st.metric(
                        label=f"Прогноз #{i+1}",
                        value=f"{group[0]} {group[1]} {group[2]} {group[3]}",
                        delta=f"{score:.4f}"
                    )
            
            # Сохраняем прогнозы
            try:
                save_predictions(st.session_state.operation_result)
                st.info("💾 Прогнозы сохранены для сравнения")
            except Exception as e:
                st.warning(f"⚠️ Не удалось сохранить прогнозы: {e}")
        else:
            st.warning("⚠️ Прогнозы не сгенерированы")
