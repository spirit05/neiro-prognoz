# [file name]: web/components/data_ui.py
"""
Интерфейс работы с данными
"""

import streamlit as st
from ml.utils.data_utils import load_dataset, save_dataset, validate_group, compare_groups, load_predictions, save_predictions
from .utils import show_operation_progress, show_recent_logs, validate_and_format_groups_input

def show_data_ui(system, run_operation_sync):
    """Показать интерфейс работы с данными"""
    
    st.header("📊 Управление данными")
    
    # Показываем последнюю группу
    try:
        dataset = load_dataset()
        if dataset:
            st.info(f"📋 **Последняя добавленная группа:** `{dataset[-1]}`")
    except:
        pass

     try:
        if system and hasattr(system, 'api_client'):
            last_entry = system.api_client.get_last_entry()
            if last_entry and 'draw' in last_entry:
                st.info(f"🎯 **Последний добавленный тираж:** `{last_entry['draw']}`")
            else:
                st.info("📝 **Последний тираж:** информация отсутствует")
    except Exception as e:
        st.info("📝 **Последний тираж:** не удалось загрузить")

    # Создаем две колонки для разделения функционала
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("➕ Добавить одну группу")
        st.info("""
        **Добавление с дообучением:**
        - Введите 4 числа от 1 до 26 через пробел
        - Система сравнит с предыдущими прогнозами
        - Выполнит дообучение
        - **Время: 3-7 минут**
        """)
        
        # Поле ввода одной группы
        single_group_input = st.text_input(
            "Одна группа:",
            placeholder="1 9 22 19",
            help="4 числа через пробел, от 1 до 26",
            key="single_group"
        )
        
        # Кнопка добавления одной группы
        if st.button("✅ Добавить и дообучить", type="primary", key="add_single"):
            _process_single_group(system, run_operation_sync, single_group_input)
    
    with col2:
        st.subheader("📝 Добавить несколько групп")
        st.info("""
        **Добавление с полным переобучением:**
        - Введите несколько групп (каждая с новой строки)
        - Формат: номер_тиража дата комбинация
        - Выполнит полное переобучение
        - **Время: 5-10 минут**
        """)
        
        # Textarea для нескольких групп
        multiple_groups_input = st.text_area(
            "Несколько групп:",
            placeholder="309406 09.11.2025 15:12 26,24,18,17\n309405 09.11.2025 14:57 4,23,17,18",
            help="Каждая группа с новой строки. Формат: номер дата время комбинация",
            height=120,
            key="multiple_groups"
        )
        
        # Кнопка добавления нескольких групп
        if st.button("🔄 Добавить и переобучить", type="secondary", key="add_multiple"):
            _process_multiple_groups(system, run_operation_sync, multiple_groups_input)

def _process_single_group(system, run_operation_sync, sequence_input):
    """Обработка одной группы"""
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

        last_info_entry = system.api_client.get_last_entry().get('draw')
        next_info_entry = int(last_info_entry) + 1
        system.api_client._save_info(next_info_entry, sequence_input)
        
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

            if hasattr(st.session_state, 'operation_result') and st.session_state.operation_result:
                # Анализ точности
                learning_system = SelfLearningSystem()
                analysis_result = learning_system.analyze_prediction_accuracy(sequence_input)            

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

def _process_multiple_groups(system, run_operation_sync, groups_input):
    """Обработка нескольких групп"""
    if not system:
        st.error("❌ Система не инициализирована")
        return
        
    if not groups_input:
        st.error("❌ Введите группы")
        return        
        
    try:
        group_list = validate_and_format_groups_input(groups_input)
        if not group_list:
            st.error("❌ Неверный формат! Должно быть 4 числа 1-26 через пробел")
            return
        
        last_entry = system.api_client.get_last_entry()
        if not last_entry:  # Если None или пустой словарь
            st.error("❌ Нет данных о последнем тираже!")
            return
            
        last_info_entry = int(last_entry.get('draw')) + 1 
        if not last_info_entry:  # Если draw нет или пустой
            st.error("❌ Не удалось получить номер последнего тиража!")
            return

        group_info_entry = int(group_list[0].get('draw'))

        if last_info_entry != group_info_entry:
            st.error("❌ Неверный номер тиража!")
            return
   
        st.info("✅ Тираж верный")

        # Загружаем и обновляем данные
        dataset = load_dataset()
        old_count = len(dataset)

        for group in group_list:
            combination = group.get('combination')
            draw = group.get('draw')
            dataset.append(combination)
            system.api_client._save_info(draw, combination)

        new_count = len(dataset)
        save_dataset(dataset)

        st.info("✅ Данные сохранены")
        
        # Запускаем операцию СИНХРОННО
        with st.spinner("🔄 Запуск обучения..."):
            result = run_operation_sync("training")
        
        # Показываем результат
        if hasattr(st.session_state, 'operation_error') and st.session_state.operation_error:
            st.error(f"❌ Ошибка обучения: {st.session_state.operation_error}")
        elif hasattr(st.session_state, 'operation_result') and st.session_state.operation_result:
            st.balloons()
            st.success("🎉 Обучение успешно завершено!")
            
            # Показываем логи если есть
            if hasattr(st.session_state, 'progress_messages') and st.session_state.progress_messages:
                show_recent_logs(st.session_state.progress_messages, max_logs=5)
            
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
            
    except Exception as e:
        st.error(f"❌ Ошибка: {e}")
