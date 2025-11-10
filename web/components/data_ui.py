# [file name]: web/components/data_ui.py
"""
Интерфейс работы с данными
"""

import streamlit as st
from ml.utils.data_utils import load_dataset, save_dataset, validate_group, compare_groups, load_predictions, save_predictions
from .utils import show_operation_progress, show_recent_logs

def show_data_ui(system, run_operation_sync):
    """Показать интерфейс работы с данными"""
    st.header("➕ Добавить новую группу")
    
    # Показываем последнюю группу
    try:
        dataset = load_dataset()
        if dataset:
            st.info(f"📋 **Последняя добавленная группа:** `{dataset[-1]}`")
    except:
        pass
    
    st.info("""
    **Добавление новой группы с дообучением:**
    - Введите 4 числа от 1 до 26 через пробел
    - Система сравнит с предыдущими прогнозами
    - Выполнит дообучение на новых данных
    - Сгенерирует обновленные прогнозы
    - **Время: 3-7 минут**
    """)
    
    # Поле ввода
    sequence_input = st.text_input(
        "Числовая последовательность:",
        placeholder="1 9 22 19",
        help="Пример: 1 9 22 19 - 4 числа через пробел, от 1 до 26"
    )
    
    # Кнопка добавления
    if st.button("✅ Добавить и дообучить", type="primary"):
        if not system:
            st.error("❌ Система не инициализирована")
            return
            
        if not sequence_input:
            st.error("❌ Введите последовательность")
            return
            
        try:
            if not validate_group(sequence_input):
                st.error("❌ Неверный формат! Должно быть 4 числа 1-26 через пробел")
                return
            
            # Сравнение с предыдущими прогнозами
            sequence_numbers = [int(x) for x in sequence_input.strip().split()]
            sequence_tuple = tuple(sequence_numbers)
            previous_predictions = load_predictions()
            
            if previous_predictions:
                matches_found = []
                for pred_group, score in previous_predictions:
                    comparison = compare_groups(pred_group, sequence_tuple)
                    if comparison['total_matches'] > 0:
                        matches_found.append((pred_group, comparison))
                
                if matches_found:
                    st.success(f"🔍 Найдено совпадений с {len(matches_found)} предсказаниями:")
                    for i, (pred_group, comparison) in enumerate(matches_found[:3], 1):
                        st.write(f"**{i}.** Прогноз: `{pred_group[0]} {pred_group[1]} {pred_group[2]} {pred_group[3]}`")
                        st.write(f"   - Совпадения по парам: **{comparison['total_matches']}/4**")
                else:
                    st.info("📝 Совпадений с предыдущими прогнозами нет")
            else:
                st.info("📝 Нет предыдущих прогнозов для сравнения")
            
            st.markdown("---")
            
            # Показываем ожидаемые этапы
            st.subheader("📋 План операции:")
            show_operation_progress("add_data", 0, 5)
            
            # Запускаем операцию СИНХРОННО
            with st.spinner("🔄 Обработка данных..."):
                result = run_operation_sync("add_data", sequence_input=sequence_input)
            
            # Показываем результат
            if hasattr(st.session_state, 'operation_error') and st.session_state.operation_error:
                st.error(f"❌ Ошибка при обработке: {st.session_state.operation_error}")
            elif hasattr(st.session_state, 'operation_result') and st.session_state.operation_result:
                st.balloons()
                st.success("🎉 Группа добавлена и модель дообучена!")
                
                # Показываем завершенные этапы
                show_operation_progress("add_data", 5, 5, "Обработка завершена!")
                
                # Показываем логи если есть
                if hasattr(st.session_state, 'progress_messages') and st.session_state.progress_messages:
                    show_recent_logs(st.session_state.progress_messages, max_logs=5)
                
                # Сохраняем прогнозы
                try:
                    save_predictions(st.session_state.operation_result)
                    st.info("💾 Новые прогнозы сохранены в кэш")
                except Exception as e:
                    st.warning(f"⚠️ Не удалось сохранить прогнозы: {e}")
                
                # Показываем новые прогнозы
                st.subheader("🎯 Обновленные прогнозы")
                for i, (group, score) in enumerate(st.session_state.operation_result[:4], 1):
                    confidence = "🟢 ВЫСОКАЯ" if score > 0.01 else "🟡 СРЕДНЯЯ" if score > 0.001 else "🔴 НИЗКАЯ"
                    st.write(f"**{i}.** `{group[0]} {group[1]} {group[2]} {group[3]}`")
                    st.write(f"   Уверенность: `{score:.6f}` {confidence}")
            else:
                st.warning("⚠️ Обработка завершена, но новые прогнозы не получены")
                
        except Exception as e:
            st.error(f"❌ Ошибка: {e}")
