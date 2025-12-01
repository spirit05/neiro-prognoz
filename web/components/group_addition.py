# [file name]: web/components/group_addition.py
"""
Добавление новых групп данных - ИСПРАВЛЕННЫЕ ИМПОРТЫ ДЛЯ НОВОЙ АРХИТЕКТУРЫ
"""

import streamlit as st
from web.core.state_manager import StateManager
from ml.data.providers.dataset_manager import DatasetManager
from ml.data.quality.validators import DataValidator
from .styles import create_info_box, create_warning_box, create_success_box


class GroupAddition:
    """Компонент добавления групп данных"""
    
    def __init__(self):
        self.dataset_manager = DatasetManager()
        self.validator = DataValidator()
    
    @staticmethod
    def render():
        """Рендеринг интерфейса добавления групп"""
        st.header("➕ Добавление групп данных")
        
        system = StateManager.get_ml_system()
        if system is None:
            st.error("❌ Система не инициализирована")
            return
        
        # Создаем экземпляр с менеджерами
        group_addition = GroupAddition()
        
        # Создаем две колонки для разделения функционала
        col1, col2 = st.columns(2)
        
        with col1:
            group_addition._render_single_group_interface(system)
        
        with col2:
            group_addition._render_multiple_groups_interface(system)
        
        # Показываем прогресс если операция выполняется
        if StateManager.is_operation_in_progress():
            group_addition._render_addition_progress()
        
        # Показываем результат последней операции
        group_addition._render_operation_result()
    
    def _render_single_group_interface(self, system):
        """Рендеринг интерфейса добавления одной группы"""
        st.subheader("➕ Добавить одну группу")
        
        create_info_box(
            "Добавление с дообучением",
            "**Добавление с дообучением:**\n"
            "- Введите 4 числа от 1 до 26 через пробел\n"
            "- Система сравнит с предыдущими прогнозами\n"
            "- Выполнит дообучение\n"
            "- **Время: 3-7 минут**"
        )
        
        # Поле ввода одной группы
        single_group_input = st.text_input(
            "Одна группа:",
            placeholder="1 9 22 19",
            help="4 числа через пробел, от 1 до 26",
            key="single_group"
        )
        
        # Кнопка добавления одной группы
        if st.button("✅ Добавить и дообучить", type="primary", key="add_single", use_container_width=True):
            self._process_single_group(system, single_group_input)
    
    def _render_multiple_groups_interface(self, system):
        """Рендеринг интерфейса добавления нескольких групп"""
        st.subheader("📝 Добавить несколько групп")
        
        create_info_box(
            "Добавление с переобучением",
            "**Добавление с полным переобучением:**\n"
            "- Введите несколько групп (каждая с новой строки)\n"
            "- Формат: 4 числа через пробел\n"
            "- Выполнит полное переобучение\n"
            "- **Время: 5-10 минут**"
        )
        
        # Textarea для нескольких групп
        multiple_groups_input = st.text_area(
            "Несколько групп:",
            placeholder="1 2 3 4\n5 6 7 8\n9 10 11 12",
            help="Каждая группа с новой строки. Формат: 4 числа через пробел",
            height=120,
            key="multiple_groups"
        )
        
        # Выбор стратегии
        strategy = st.selectbox(
            "Стратегия обработки:",
            ["full_retrain", "incremental"],
            format_func=lambda x: "Полное переобучение" if x == "full_retrain" else "Инкрементальное обучение",
            help="Стратегия обучения после добавления данных"
        )
        
        # Кнопка добавления нескольких групп
        if st.button("🔄 Добавить и переобучить", type="secondary", key="add_multiple", use_container_width=True):
            self._process_multiple_groups(system, multiple_groups_input, strategy)
    
    def _process_single_group(self, system, group_input):
        """Обработка одной группы"""
        if not group_input:
            st.error("❌ Введите последовательность")
            return
        
        try:
            # Валидация группы через DataValidator новой архитектуры
            if not self.validator.validate_group(group_input):
                st.error("❌ Неверный формат! Должно быть 4 числа 1-26 через пробел")
                return
            
            # Преобразуем ввод в список чисел
            group_numbers = [int(x) for x in group_input.strip().split()]
            
            # Пока пропускаем сравнение с прогнозами, так как в новой архитектуре
            # эта функциональность может быть в другом месте
            st.markdown("---")
            
            # Запускаем workflow добавления одной группы
            self._run_single_group_workflow(system, group_numbers)
            
        except Exception as e:
            st.error(f"❌ Ошибка при обработке группы: {e}")
    
    def _process_multiple_groups(self, system, groups_input, strategy):
        """Обработка нескольких групп"""
        if not groups_input:
            st.error("❌ Введите группы")
            return
        
        try:
            # Разбираем ввод
            lines = [line.strip() for line in groups_input.split('\n') if line.strip()]
            valid_groups = []
            invalid_groups = []
            
            for line in lines:
                if self.validator.validate_group(line):
                    group_numbers = [int(x) for x in line.strip().split()]
                    valid_groups.append(group_numbers)
                else:
                    invalid_groups.append(line)
            
            if not valid_groups:
                st.error("❌ Не найдено валидных групп! Проверьте формат.")
                return
            
            if invalid_groups:
                st.warning(f"⚠️ Пропущено {len(invalid_groups)} невалидных групп")
                for invalid in invalid_groups[:3]:  # Показываем первые 3
                    st.write(f"`{invalid}`")
            
            st.success(f"✅ Найдено {len(valid_groups)} валидных групп для добавления")
            
            # Запускаем workflow добавления нескольких групп
            self._run_multiple_groups_workflow(system, valid_groups, strategy)
            
        except Exception as e:
            st.error(f"❌ Ошибка при обработке групп: {e}")
    
    def _run_single_group_workflow(self, system, group):
        """Запуск workflow для одной группы"""
        try:
            StateManager.set_operation_in_progress(True)
            StateManager.clear_progress_messages()
            StateManager.add_progress_message(f"🔄 Добавление группы {group} через WorkflowManager...")
            
            # Запускаем добавление одной группы
            result = system.add_single_group(group)
            
            # Обрабатываем результат
            if result.status == "completed":
                StateManager.set_operation_result(result)
                StateManager.add_progress_message("✅ Группа успешно добавлена и модель дообучена!")
                
            else:
                error_msg = f"❌ Ошибка добавления группы: {result.error}"
                StateManager.set_operation_error(error_msg)
                StateManager.add_progress_message(error_msg)
                
        except Exception as e:
            error_msg = f"❌ Критическая ошибка при добавлении группы: {e}"
            StateManager.set_operation_error(error_msg)
            StateManager.add_progress_message(error_msg)
        finally:
            StateManager.set_operation_in_progress(False)
    
    def _run_multiple_groups_workflow(self, system, groups, strategy):
        """Запуск workflow для нескольких групп"""
        try:
            StateManager.set_operation_in_progress(True)
            StateManager.clear_progress_messages()
            StateManager.add_progress_message(f"🔄 Добавление {len(groups)} групп через WorkflowManager...")
            
            # Запускаем добавление нескольких групп
            result = system.add_multiple_groups(groups, strategy)
            
            # Обрабатываем результат
            if result.status == "completed":
                StateManager.set_operation_result(result)
                StateManager.add_progress_message(f"✅ {len(groups)} групп успешно добавлены!")
                
            else:
                error_msg = f"❌ Ошибка добавления групп: {result.error}"
                StateManager.set_operation_error(error_msg)
                StateManager.add_progress_message(error_msg)
                
        except Exception as e:
            error_msg = f"❌ Критическая ошибка при добавлении групп: {e}"
            StateManager.set_operation_error(error_msg)
            StateManager.add_progress_message(error_msg)
        finally:
            StateManager.set_operation_in_progress(False)
    
    def _render_addition_progress(self):
        """Рендеринг прогресса добавления данных"""
        st.subheader("📊 Ход обработки данных")
        
        # Прогресс-бар
        progress = st.progress(0)
        
        # Показываем сообщения прогресса
        messages = StateManager.get_progress_messages()
        if messages:
            recent_messages = messages[-8:]  # Последние 8 сообщений
            st.text_area(
                "📝 Детали выполнения:", 
                "\n".join(recent_messages), 
                height=150,
                key="addition_progress"
            )
        
        # Обновляем прогресс на основе сообщений
        if any("валидация" in msg.lower() for msg in messages):
            progress.progress(20)
        elif any("добавлен" in msg.lower() for msg in messages):
            progress.progress(40)
        elif any("обучен" in msg.lower() for msg in messages):
            progress.progress(60)
        elif any("прогноз" in msg.lower() for msg in messages):
            progress.progress(80)
        elif any("завершен" in msg.lower() for msg in messages):
            progress.progress(100)
    
    def _render_operation_result(self):
        """Рендеринг результата операции"""
        result = StateManager.get_operation_result()
        error = StateManager.get_operation_error()
        
        if error:
            st.error(f"❌ {error}")
        
        elif result:
            create_success_box(
                "Операция завершена!",
                f"**Статус:** {result.status}\n"
                f"**Сообщение:** {result.message}\n"
                f"**Время выполнения:** {result.execution_time:.2f} секунд\n"
                f"**Выполненные этапы:** {', '.join(result.steps_completed)}"
            )
            
            # Показываем дополнительные данные если есть
            if result.data:
                st.subheader("📈 Результаты операции")
                
                if 'group_added' in result.data:
                    st.success(f"✅ Добавлена группа: `{result.data['group_added']}`")
                
                if 'groups_added' in result.data:
                    st.success(f"✅ Добавлено групп: {result.data['groups_added']}")
                
                if 'strategy' in result.data:
                    strategy_name = "Полное переобучение" if result.data['strategy'] == "full_retrain" else "Инкрементальное обучение"
                    st.info(f"🏗️ Использованная стратегия: {strategy_name}")
                
                if 'training_metrics' in result.data:
                    st.info("📊 Метрики обучения обновлены")
                
                if 'predictions_generated' in result.data:
                    st.info(f"🔮 Сгенерировано прогнозов: {result.data['predictions_generated']}")
