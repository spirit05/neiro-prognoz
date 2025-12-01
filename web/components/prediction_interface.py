# [file name]: web/components/prediction_interface.py
"""
Интерфейс генерации прогнозов
"""

import streamlit as st
from web.core.state_manager import StateManager
from .styles import create_info_box, create_success_box


class PredictionInterface:
    """Компонент интерфейса прогнозирования"""
    
    @staticmethod
    def render():
        """Рендеринг интерфейса прогнозов"""
        st.header("🔮 Генерация прогнозов")
        
        system = StateManager.get_ml_system()
        if system is None:
            st.error("❌ Система не инициализирована")
            return
        
        create_info_box(
            "AI прогнозирование",
            "**AI проанализирует паттерны и сгенерирует прогнозы:**\n"
            "- Использует обученную модель\n"
            "- Применяет ансамблевые методы\n"
            "- Учитывает исторические паттерны\n"
            "- **Время: 2-5 минут**"
        )
        
        # Проверяем что модель обучена
        status = system.get_system_status()
        if not status.get('is_trained', False):
            st.error("""
            ❌ **Модель не обучена!**
            Перед генерацией прогнозов необходимо обучить модель.
            Перейдите в раздел "🧠 Обучение модели".
            """)
            return
        
        # Настройки прогнозирования
        st.subheader("⚙️ Настройки прогнозирования")
        
        col1, col2 = st.columns(2)
        
        with col1:
            num_predictions = st.slider(
                "Количество прогнозов:",
                min_value=1,
                max_value=20,
                value=10,
                help="Сколько прогнозов сгенерировать"
            )
        
        with col2:
            confidence_threshold = st.slider(
                "Порог уверенности:",
                min_value=0.0,
                max_value=1.0,
                value=0.1,
                step=0.01,
                help="Минимальная уверенность для показа прогноза"
            )
        
        # Кнопка генерации прогнозов
        if st.button("🎯 Сгенерировать прогнозы", type="primary", use_container_width=True):
            PredictionInterface._run_prediction_workflow(system)
        
        # Показываем прогресс если операция выполняется
        if StateManager.is_operation_in_progress():
            PredictionInterface._render_prediction_progress()
        
        # Показываем результат последней операции
        PredictionInterface._render_operation_result()
        
        # Показываем исторические прогнозы
        PredictionInterface._render_historical_predictions()
    
    @staticmethod
    def _run_prediction_workflow(system):
        """Запуск workflow прогнозирования"""
        try:
            StateManager.set_operation_in_progress(True)
            StateManager.clear_progress_messages()
            StateManager.add_progress_message("🔄 Запуск генерации прогнозов через WorkflowManager...")
            
            # Запускаем генерацию прогнозов
            result = system.generate_predictions()
            
            # Обрабатываем результат
            if result.status == "completed":
                StateManager.set_operation_result(result)
                StateManager.add_progress_message("✅ Прогнозы успешно сгенерированы!")
                
                # Сохраняем информацию о прогнозах
                if result.data and 'predictions_generated' in result.data:
                    StateManager.add_progress_message(f"📊 Сгенерировано {result.data['predictions_generated']} прогнозов")
                
            else:
                error_msg = f"❌ Ошибка генерации прогнозов: {result.error}"
                StateManager.set_operation_error(error_msg)
                StateManager.add_progress_message(error_msg)
                
        except Exception as e:
            error_msg = f"❌ Критическая ошибка при генерации прогнозов: {e}"
            StateManager.set_operation_error(error_msg)
            StateManager.add_progress_message(error_msg)
        finally:
            StateManager.set_operation_in_progress(False)
    
    @staticmethod
    def _render_prediction_progress():
        """Рендеринг прогресса генерации прогнозов"""
        st.subheader("📊 Ход генерации прогнозов")
        
        # Показываем этапы
        steps = [
            "📊 Анализ истории данных...",
            "🧠 Применение моделей...",
            "🏗️ Ансамблевое предсказание...", 
            "📈 Расчет уверенности...",
            "💾 Сохранение прогнозов..."
        ]
        
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
                key="prediction_progress"
            )
        
        # Обновляем прогресс на основе сообщений
        if any("анализ" in msg.lower() for msg in messages):
            progress.progress(20)
        elif any("модел" in msg.lower() for msg in messages):
            progress.progress(40)
        elif any("ансамбл" in msg.lower() for msg in messages):
            progress.progress(60)
        elif any("уверен" in msg.lower() for msg in messages):
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
                "Прогнозы сгенерированы!",
                f"**Статус:** {result.status}\n"
                f"**Сообщение:** {result.message}\n"
                f"**Время выполнения:** {result.execution_time:.2f} секунд"
            )
            
            # Показываем дополнительные данные если есть
            if result.data:
                st.subheader("🎯 Результаты прогнозирования")
                
                col1, col2, col3 = st.columns(3)
                
                with col1:
                    if 'predictions_generated' in result.data:
                        st.metric("🔮 Сгенерировано прогнозов", result.data['predictions_generated'])
                
                with col2:
                    if 'models_used' in result.data:
                        st.metric("🧠 Использовано моделей", len(result.data['models_used']))
                
                with col3:
                    if 'source_groups' in result.data:
                        st.metric("📊 Источник данных", f"{len(result.data['source_groups'])} групп")
    
    @staticmethod
    def _render_historical_predictions():
        """Рендеринг исторических прогнозов"""
        st.subheader("📜 Последние прогнозы")
        
        # Здесь можно загрузить и отобразить последние прогнозы из базы
        # Показываем сообщение что функционал в разработке
        st.info("""
        **Исторические прогнозы**
        Этот раздел будет отображать историю всех сгенерированных прогнозов
        с возможностью фильтрации и анализа.
        """)
