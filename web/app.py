# /opt/dev/web/app.py
"""
Главный веб-интерфейс для новой архитектуры - ИНТЕГРИРОВАННАЯ ВЕРСИЯ
"""
import streamlit as st
import time
import logging
from datetime import datetime

# Импорты из новой архитектуры
from integration.core import get_integration_manager
from utils.data_helpers import (
    load_dataset, save_predictions, load_predictions, 
    validate_group, compare_groups
)

# Настройка логирования
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Инициализация session_state
if 'integration_manager' not in st.session_state:
    st.session_state.integration_manager = None
if 'system_initialized' not in st.session_state:
    st.session_state.system_initialized = False
if 'progress_messages' not in st.session_state:
    st.session_state.progress_messages = []
if 'operation_running' not in st.session_state:
    st.session_state.operation_running = False

def init_system():
    """Инициализация системы"""
    if st.session_state.system_initialized:
        return True
    
    try:
        with st.spinner("🔄 Инициализация AI системы..."):
            st.session_state.integration_manager = get_integration_manager()
            st.session_state.system_initialized = True
        
        st.success("✅ Система успешно инициализирована")
        return True
        
    except Exception as e:
        st.error(f"❌ Ошибка инициализации системы: {e}")
        return False

def show_system_status():
    """Показать статус системы"""
    st.sidebar.header("📊 Статус системы")
    
    if not st.session_state.system_initialized:
        st.sidebar.error("❌ Система не инициализирована")
        return
    
    try:
        status = st.session_state.integration_manager.get_system_status()
        
        # Основной статус
        st.sidebar.info(f"🌍 Среда: {status['environment']}")
        
        # Статус компонентов
        if status['ml_system_initialized']:
            st.sidebar.success("✅ ML система")
        else:
            st.sidebar.error("❌ ML система")
            
        if status['predictor_initialized']:
            predictor_status = "✅" if status['predictor']['model_loaded'] else "⚠️"
            st.sidebar.info(f"{predictor_status} Предсказатель")
        
        # Данные
        dataset = load_dataset()
        st.sidebar.info(f"📁 Групп в датасете: {len(dataset)}")
        
        if len(dataset) >= 50:
            st.sidebar.success("✅ Данных достаточно")
        else:
            st.sidebar.warning(f"⚠️ Нужно больше данных")
        
        # Автосервис
        if status.get('auto_service_available'):
            auto_status = status.get('auto_service', {})
            if auto_status.get('service_active'):
                st.sidebar.success("✅ Автосервис активен")
            else:
                st.sidebar.warning("⚠️ Автосервис остановлен")
        
    except Exception as e:
        st.sidebar.error(f"Ошибка статуса: {e}")

def train_model_ui():
    """Интерфейс обучения модели"""
    st.header("🧠 Обучение модели AI")
    
    st.info("""
    **Полное обучение модели на всех данных:**
    - Использует систему самообучения
    - Загружает все доступные данные
    - Настраивает ансамблевую систему
    - **Время: 10-15 минут**
    """)
    
    if st.button("🚀 Начать обучение", type="primary", key="train_btn"):
        if not st.session_state.system_initialized:
            st.error("❌ Система не инициализирована")
            return
        
        # Проверяем данные
        dataset = load_dataset()
        if len(dataset) < 50:
            st.error(f"❌ Недостаточно данных: {len(dataset)} групп (нужно 50)")
            return
        
        with st.spinner("🔄 Запуск обучения..."):
            try:
                result = st.session_state.integration_manager.train_model()
                
                if result['success']:
                    st.balloons()
                    st.success(f"✅ {result['message']}")
                    
                    # Показываем статистику
                    col1, col2 = st.columns(2)
                    with col1:
                        st.metric("Эпохи обучения", result['epochs'])
                    with col2:
                        st.metric("Групп в датасете", result['dataset_size'])
                    
                else:
                    st.error(f"❌ Ошибка обучения: {result['error']}")
                    
            except Exception as e:
                st.error(f"❌ Ошибка обучения: {e}")

def predictions_ui():
    """Интерфейс прогнозирования"""
    st.header("🔮 Генерация прогнозов")
    
    st.info("""
    **AI проанализирует паттерны и сгенерирует прогнозы:**
    - Использует усиленный предсказатель с ансамблем
    - Учитывает исторические паттерны
    - Применяет систему самообучения
    - **Время: 2-3 минуты**
    """)
    
    # Настройки прогнозирования
    col1, col2 = st.columns(2)
    with col1:
        top_k = st.selectbox("Количество прогнозов", [4, 6, 8, 10], index=0)
    with col2:
        use_ensemble = st.checkbox("Использовать ансамбль", value=True)
    
    if st.button("🎯 Сгенерировать прогнозы", type="primary", key="predict_btn"):
        if not st.session_state.system_initialized:
            st.error("❌ Система не инициализирована")
            return
        
        # Проверяем что модель загружена
        status = st.session_state.integration_manager.get_system_status()
        if not status['predictor']['model_loaded']:
            st.error("❌ Модель не загружена! Сначала выполните обучение.")
            return
        
        with st.spinner("🔄 Анализ паттернов и генерация прогнозов..."):
            try:
                # Настраиваем ансамбль
                if st.session_state.integration_manager.predictor:
                    st.session_state.integration_manager.predictor.enable_ensemble(use_ensemble)
                
                predictions = st.session_state.integration_manager.make_predictions(top_k)
                
                if predictions:
                    st.success(f"✅ Сгенерировано {len(predictions)} прогнозов")
                    
                    # Сохраняем прогнозы
                    save_predictions(predictions)
                    
                    # Показываем прогнозы
                    st.subheader("🏆 Топ прогнозы")
                    
                    cols = st.columns(2)
                    for i, (group, score) in enumerate(predictions):
                        with cols[i % 2]:
                            confidence_level = "🟢 ВЫСОКАЯ" if score > 0.01 else "🟡 СРЕДНЯЯ" if score > 0.001 else "🔴 НИЗКАЯ"
                            
                            st.metric(
                                label=f"Прогноз #{i+1}",
                                value=f"{group[0]} {group[1]} {group[2]} {group[3]}",
                                delta=f"{score:.4f} {confidence_level}"
                            )
                else:
                    st.warning("⚠️ Прогнозы не сгенерированы")
                    
            except Exception as e:
                st.error(f"❌ Ошибка прогнозирования: {e}")

def add_data_ui():
    """Интерфейс добавления данных"""
    st.header("➕ Добавить данные и дообучить")
    
    # Показываем последнюю группу
    try:
        dataset = load_dataset()
        if dataset:
            st.info(f"📋 **Последняя группа в датасете:** `{dataset[-1]}`")
    except:
        pass
    
    st.info("""
    **Добавление новой группы с дообучением:**
    - Введите 4 числа от 1 до 26 через пробел
    - Система сравнит с предыдущими прогнозами
    - Выполнит дообучение на новых данных
    - Сгенерирует обновленные прогнозы
    - **Время: 3-5 минут**
    """)
    
    # Поле ввода
    sequence_input = st.text_input(
        "Числовая последовательность:",
        placeholder="1 9 22 19",
        help="Пример: 1 9 22 19 - 4 числа через пробел, от 1 до 26",
        key="sequence_input"
    )
    
    col1, col2 = st.columns(2)
    with col1:
        retrain_epochs = st.selectbox("Эпохи дообучения", [1, 2, 3, 5], index=2)
    
    if st.button("✅ Добавить и дообучить", type="primary", key="add_data_btn"):
        if not st.session_state.system_initialized:
            st.error("❌ Система не инициализирована")
            return
            
        if not sequence_input:
            st.error("❌ Введите последовательность")
            return
        
        # Валидация
        if not validate_group(sequence_input):
            st.error("❌ Неверный формат! Должно быть 4 уникальных числа 1-26 через пробел")
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
                    matches_found.append((pred_group, comparison, score))
            
            if matches_found:
                st.success(f"🔍 Найдено совпадений с {len(matches_found)} предсказаниями:")
                for i, (pred_group, comparison, score) in enumerate(matches_found[:3], 1):
                    st.write(f"**{i}.** Прогноз: `{pred_group[0]} {pred_group[1]} {pred_group[2]} {pred_group[3]}`")
                    st.write(f"   - Совпадения: **{comparison['total_matches']}/4**")
                    st.write(f"   - Уверенность: `{score:.6f}`")
            else:
                st.info("📝 Совпадений с предыдущими прогнозами нет")
        
        st.markdown("---")
        
        # Добавление данных и дообучение
        with st.spinner("🔄 Добавление данных и дообучение..."):
            try:
                result = st.session_state.integration_manager.add_data_and_retrain(
                    sequence_input, retrain_epochs
                )
                
                if result['success']:
                    st.balloons()
                    st.success("🎉 Данные добавлены и модель дообучена!")
                    
                    # Показываем статистику
                    col1, col2 = st.columns(2)
                    with col1:
                        st.metric("Добавленная группа", sequence_input)
                    with col2:
                        st.metric("Сгенерировано прогнозов", result['predictions_generated'])
                    
                    # Генерируем новые прогнозы
                    new_predictions = st.session_state.integration_manager.make_predictions()
                    if new_predictions:
                        save_predictions(new_predictions)
                        
                        st.subheader("🎯 Обновленные прогнозы")
                        for i, (group, score) in enumerate(new_predictions[:4], 1):
                            confidence = "🟢 ВЫСОКАЯ" if score > 0.01 else "🟡 СРЕДНЯЯ" if score > 0.001 else "🔴 НИЗКАЯ"
                            st.write(f"**{i}.** `{group[0]} {group[1]} {group[2]} {group[3]}`")
                            st.write(f"   Уверенность: `{score:.6f}` {confidence}")
                    
                else:
                    st.error(f"❌ Ошибка: {result['error']}")
                    
            except Exception as e:
                st.error(f"❌ Ошибка обработки: {e}")

def analytics_ui():
    """Интерфейс аналитики"""
    st.header("📊 Аналитика и мониторинг")
    
    if not st.session_state.system_initialized:
        st.error("❌ Система не инициализирована")
        return
    
    try:
        # Полный статус системы
        status = st.session_state.integration_manager.get_system_status()
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.subheader("🧠 ML Система")
            st.info(f"🌍 Среда: {status['environment']}")
            
            if status['ml_system_initialized']:
                st.success("✅ Система самообучения")
            else:
                st.error("❌ Система самообучения")
            
            if status['predictor_initialized']:
                predictor_status = status['predictor']
                if predictor_status['model_loaded']:
                    st.success("✅ Модель загружена")
                else:
                    st.warning("⚠️ Модель не загружена")
                
                if predictor_status['use_ensemble']:
                    st.info("✅ Ансамблевый режим")
                else:
                    st.info("🔧 Базовый режим")
        
        with col2:
            st.subheader("🔧 Сервисы")
            if status.get('auto_service_available'):
                auto_status = status.get('auto_service', {})
                if auto_status.get('service_active'):
                    st.success("✅ Автосервис активен")
                    st.info(f"🔄 Ошибок API: {auto_status.get('consecutive_api_errors', 0)}")
                else:
                    st.warning("⚠️ Автосервис остановлен")
            else:
                st.info("🔧 Автосервис не доступен")
        
        # Аналитика самообучения
        st.subheader("📈 Аналитика самообучения")
        insights = st.session_state.integration_manager.get_learning_insights()
        
        if 'error' in insights:
            st.warning(f"⚠️ {insights['error']}")
        else:
            col1, col2, col3, col4 = st.columns(4)
            
            with col1:
                if 'recent_accuracy_avg' in insights:
                    accuracy = insights['recent_accuracy_avg']
                    st.metric("🎯 Средняя точность", f"{accuracy:.1%}")
            
            with col2:
                if 'total_predictions_analyzed' in insights:
                    st.metric("📊 Проанализировано", insights['total_predictions_analyzed'])
            
            with col3:
                if 'best_accuracy' in insights:
                    best = insights['best_accuracy']
                    st.metric("🏆 Лучшая точность", f"{best:.1%}")
            
            with col4:
                if 'worst_accuracy' in insights:
                    worst = insights['worst_accuracy']
                    st.metric("📉 Худшая точность", f"{worst:.1%}")
            
            # Рекомендации
            if 'recommendations' in insights and insights['recommendations']:
                st.subheader("💡 Рекомендации системы")
                for rec in insights['recommendations']:
                    st.write(f"• {rec}")
        
        # Последние прогнозы
        st.subheader("🎯 Последние прогнозы")
        predictions = load_predictions()
        if predictions:
            for i, (group, score) in enumerate(predictions[:6], 1):
                confidence = "🟢 ВЫСОКАЯ" if score > 0.01 else "🟡 СРЕДНЯЯ" if score > 0.001 else "🔴 НИЗКАЯ"
                col1, col2 = st.columns([3, 2])
                with col1:
                    st.write(f"**{i}.** `{group[0]} {group[1]} {group[2]} {group[3]}`")
                with col2:
                    st.write(f"`{score:.6f}` {confidence}")
        else:
            st.info("📝 Прогнозы еще не сгенерированы")
            
    except Exception as e:
        st.error(f"❌ Ошибка загрузки аналитики: {e}")

def main():
    """Главная функция"""
    st.set_page_config(
        page_title="AI Prediction System - Новая Архитектура",
        page_icon="🎯",
        layout="wide",
        initial_sidebar_state="expanded"
    )
    
    st.title("🎯 AI Prediction System - Новая Архитектура")
    st.markdown("**Усиленная нейросеть с системой самообучения и модульной архитектурой**")
    
    # Инициализация системы
    if not st.session_state.system_initialized:
        init_system()
    
    # Боковая панель
    show_system_status()
    
    st.sidebar.markdown("---")
    st.sidebar.header("🧭 Навигация")
    
    menu_option = st.sidebar.selectbox(
        "Выберите раздел:",
        ["📊 Аналитика", "🧠 Обучение", "🔮 Прогнозы", "➕ Добавить данные"]
    )
    
    # Основной контент
    if menu_option == "📊 Аналитика":
        analytics_ui()
    elif menu_option == "🧠 Обучение":
        train_model_ui()
    elif menu_option == "🔮 Прогнозы":
        predictions_ui()
    elif menu_option == "➕ Добавить данные":
        add_data_ui()

if __name__ == "__main__":
    main()