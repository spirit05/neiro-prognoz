# [file name]: web/components/training_control.py
"""
Управление обучением модели
"""

import streamlit as st
import time
from web.core.state_manager import StateManager
from .styles import create_info_box, create_warning_box, create_success_box


class TrainingControl:
    """Компонент управления обучением модели"""
    
    @staticmethod
    def render():
        """Рендеринг интерфейса обучения"""
        st.header("🧠 Обучение модели AI")
        
        system = StateManager.get_ml_system()
        if system is None:
            st.error("❌ Система не инициализирована")
            return
        
        # Информация о обучении
        col1, col2 = st.columns([2, 1])
        
        with col1:
            create_info_box(
                "Полное обучение модели",
                "**Полное обучение модели на всех данных:**\n"
                "- Анализ всех доступных групп чисел\n"
                "- Создание ансамблевой системы\n"
                "- Генерация первых прогнозов\n"
                "- **Время: 15-20 минут**"
            )
        
        with col2:
            create_warning_box(
                "Внимание",
                "**⚠️ Внимание:**\n"
                "Не закрывайте страницу во время обучения!"
            )
        
        # Проверяем статус системы
        status = system.get_system_status()
        if not status.get('has_sufficient_data', False):
            st.warning("""
            ⚠️ **Мало данных для обучения!**
            Рекомендуется иметь минимум 50 групп данных.
            Текущее количество: {}
            """.format(status.get('dataset_size', 0)))
        
        # Кнопка запуска обучения
        if st.button("🚀 Начать полное обучение", type="primary", use_container_width=True):
            TrainingControl._run_training_workflow(system)
        
        # Показываем прогресс если операция выполняется
        if StateManager.is_operation_in_progress():
            TrainingControl._render_training_progress()
        
        # Показываем результат последней операции
        TrainingControl._render_operation_result()
    
    @staticmethod
    def _run_training_workflow(system):
        """Запуск workflow обучения"""
        try:
            StateManager.set_operation_in_progress(True)
            StateManager.clear_progress_messages()
            StateManager.add_progress_message("🔄 Запуск полного обучения через WorkflowManager...")
            
            # Запускаем обучение
            result = system.run_full_training()
            
            # Обрабатываем результат
            if result.status == "completed":
                StateManager.set_operation_result(result)
                StateManager.add_progress_message("✅ Обучение успешно завершено!")
                
                # Сохраняем прогнозы если они есть в результате
                if result.data and 'predictions_generated' in result.data:
                    StateManager.add_progress_message(f"📊 Сгенерировано {result.data['predictions_generated']} прогнозов")
                
            else:
                error_msg = f"❌ Ошибка обучения: {result.error}"
                StateManager.set_operation_error(error_msg)
                StateManager.add_progress_message(error_msg)
                
        except Exception as e:
            error_msg = f"❌ Критическая ошибка при обучении: {e}"
            StateManager.set_operation_error(error_msg)
            StateManager.add_progress_message(error_msg)
        finally:
            StateManager.set_operation_in_progress(False)
    
    @staticmethod
    def _render_training_progress():
        """Рендеринг прогресса обучения"""
        st.subheader("📊 Ход обучения")
        
        # Показываем этапы обучения
        steps = [
            "📊 Загрузка и подготовка данных...",
            "🧠 Обучение нейросети...", 
            "🏗️ Создание ансамблевой системы...",
            "🔮 Генерация прогнозов...",
            "💾 Сохранение модели и результатов..."
        ]
        
        # Прогресс-бар
        progress = st.progress(0)
        
        # Показываем сообщения прогресса
        messages = StateManager.get_progress_messages()
        if messages:
            recent_messages = messages[-10:]  # Последние 10 сообщений
            st.text_area(
                "📝 Детали выполнения:", 
                "\n".join(recent_messages), 
                height=200,
                key="training_progress"
            )
        
        # Обновляем прогресс на основе сообщений
        if any("загрузка" in msg.lower() for msg in messages):
            progress.progress(20)
        elif any("обучение" in msg.lower() for msg in messages):
            progress.progress(40)
        elif any("ансамбл" in msg.lower() for msg in messages):
            progress.progress(60)
        elif any("прогноз" in msg.lower() for msg in messages):
            progress.progress(80)
        elif any("сохранен" in msg.lower() for msg in messages):
            progress.progress(100)
    
    @staticmethod
    def _render_operation_result():
        """Рендеринг результата операции"""
        result = StateManager.get_operation_result()
        error = StateManager.get_operation_error()
        
        if error:
            st.error(f"❌ {error}")
        
        elif result:
            create_success_box(
                "Обучение завершено!",
                f"**Статус:** {result.status}\n"
                f"**Сообщение:** {result.message}\n"
                f"**Время выполнения:** {result.execution_time:.2f} секунд\n"
                f"**Выполненные этапы:** {', '.join(result.steps_completed)}"
            )
            
            # Показываем дополнительные данные если есть
            if result.data:
                st.subheader("📈 Результаты обучения")
                
                col1, col2 = st.columns(2)
                
                with col1:
                    if 'models_trained' in result.data:
                        st.metric("🧠 Обучено моделей", result.data['models_trained'])
                    
                    if 'predictions_generated' in result.data:
                        st.metric("🔮 Сгенерировано прогнозов", result.data['predictions_generated'])
                
                with col2:
                    if 'training_results' in result.data:
                        training_results = result.data['training_results']
                        st.metric("📊 Результаты обучения", f"{len(training_results)} моделей")
                        
                        # Показываем метрики для каждой модели
                        for model_id, metrics in training_results.items():
                            with st.expander(f"Модель: {model_id}"):
                                if isinstance(metrics, dict) and 'metrics' in metrics:
                                    for metric_name, value in metrics['metrics'].items():
                                        st.write(f"**{metric_name}:** {value:.4f}")
