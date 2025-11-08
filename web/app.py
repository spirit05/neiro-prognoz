# [file name]: web/app.py
#!/usr/bin/env python3
import sys
import os
import logging

# ⚡ ПУТИ НОВОЙ АРХИТЕКТУРЫ
sys.path.insert(0, '/opt/dev')

# ⚡ ИМПОРТЫ ИЗ НОВОЙ АРХИТЕКТУРЫ
try:
    from web.components import (
        MLSystemAdapter, show_sidebar, show_training_ui, 
        show_prediction_ui, show_data_ui, show_status_ui,
        apply_custom_styles, create_info_box
    )
    from ml.utils.data_utils import load_dataset, save_dataset, validate_group, compare_groups, save_predictions, load_predictions
    print("✅ Все импорты из новой архитектуры успешны")
except ImportError as e:
    print(f"❌ Ошибка импорта из новой архитектуры: {e}")
    print(f"🔍 sys.path: {sys.path}")
    raise

# Остальные импорты
import streamlit as st
import time
import uuid
from datetime import datetime

# Настройка логирования
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger('SequencePredictorWeb')

# Применяем кастомные стили
apply_custom_styles()

st.set_page_config(
    page_title="AI Прогноз Последовательностей - МОДУЛЬНАЯ АРХИТЕКТУРА", 
    page_icon="🔢", 
    layout="wide"
)

# Инициализация session_state
if 'system_initialized' not in st.session_state:
    st.session_state.system_initialized = False
if 'system' not in st.session_state:
    st.session_state.system = None
if 'progress_messages' not in st.session_state:
    st.session_state.progress_messages = []
if 'operation_running' not in st.session_state:
    st.session_state.operation_running = False
if 'operation_result' not in st.session_state:
    st.session_state.operation_result = None
if 'operation_error' not in st.session_state:
    st.session_state.operation_error = None
if 'session_id' not in st.session_state:
    st.session_state.session_id = str(uuid.uuid4())[:8]

def init_system():
    """Инициализация системы с новой архитектурой"""
    if st.session_state.system_initialized and st.session_state.system:
        return True
        
    try:
        logger.info("Инициализация ML системы с новой модульной архитектурой...")
        st.session_state.system = MLSystemAdapter()
        st.session_state.system.set_progress_callback(progress_callback)
        st.session_state.system_initialized = True
        logger.info("✅ ML система успешно инициализирована (НОВАЯ АРХИТЕКТУРА)")
        return True
    except Exception as e:
        logger.error(f"❌ Ошибка инициализации системы: {e}")
        st.error(f"❌ Ошибка инициализации системы: {e}")
        return False

def progress_callback(message):
    """Callback для отображения прогресса"""
    timestamp = datetime.now().strftime('%H:%M:%S')
    formatted_message = f"{timestamp} - {message}"
    st.session_state.progress_messages.append(formatted_message)
    logger.info(f"📢 {message}")

def run_operation_sync(operation_type, **kwargs):
    """СИНХРОННЫЙ запуск операции (без потоков) - ОБНОВЛЕННЫЙ ДЛЯ НОВОЙ АРХИТЕКТУРЫ"""
    try:
        # ⚡ ОТЛАДОЧНЫЙ ЛОГ ДЛЯ НОВОЙ АРХИТЕКТУРЫ
        debug_msg = f"🎯 НОВАЯ АРХИТЕКТУРА: Запуск операции {operation_type}"
        print(debug_msg)
        
        # Очищаем предыдущие сообщения
        st.session_state.progress_messages = []
        
        if operation_type == "training":
            logger.info("🎯 Запуск обучения в новой архитектуре")
            result = st.session_state.system.train(epochs=20)
            logger.info("✅ Обучение успешно завершено")
            
        elif operation_type == "prediction":
            logger.info("🎯 Запуск прогнозирования в новой архитектуре")
            result = st.session_state.system.predict(top_k=4)
            logger.info(f"✅ Прогнозирование завершено, получено {len(result) if result else 0} прогнозов")
            
        elif operation_type == "add_data":
            sequence_input = kwargs.get('sequence_input', '')
            logger.info("🎯 Запуск добавления данных в новой архитектуре")
            result = st.session_state.system.add_data_and_retrain(sequence_input, retrain_epochs=3)
            logger.info(f"✅ Добавление данных завершено, получено {len(result) if result else 0} прогнозов")
            
        else:
            raise ValueError(f"Неизвестный тип операции: {operation_type}")
        
        st.session_state.operation_result = result
        st.session_state.operation_error = None
        return result
        
    except Exception as e:
        logger.error(f"❌ Ошибка в операции {operation_type}: {e}")
        st.session_state.operation_result = None
        st.session_state.operation_error = str(e)
        return None

def show_progress_ui(operation_name):
    """Показ UI прогресса"""
    from web.components import show_progress_messages
    
    create_info_box("Выполняется операция", f"**{operation_name}** - пожалуйста, не закрывайте страницу")
    
    # Показываем сообщения прогресса
    show_progress_messages(st.session_state.progress_messages, height=200)
    
    # Обновляем страницу для показа новых сообщений
    time.sleep(2)
    st.rerun()

def main():
    # Заголовок с улучшенным стилем
    st.markdown('<h1 class="main-header">🔢 AI Прогноз Числовых Последовательностей</h1>', unsafe_allow_html=True)
    
    # Инициализация системы
    if not st.session_state.system_initialized:
        with st.spinner("🔄 Инициализация ML системы (НОВАЯ АРХИТЕКТУРА)..."):
            if not init_system():
                st.error("❌ Не удалось инициализировать систему. Проверьте логи для деталей.")
                return

    # Боковая панель с меню
    show_sidebar(st.session_state.system)
    
    st.sidebar.markdown("---")
    st.sidebar.header("🧭 Навигация")
    
    menu_option = st.sidebar.selectbox(
        "Выберите действие:",
        ["Обзор данных", "Обучить модель", "Получить прогнозы", "Добавить группу"]
    )
    
    # Основной контент с использованием модульных компонентов
    if menu_option == "Обзор данных":
        show_status_ui(st.session_state.system)
    elif menu_option == "Обучить модель":
        show_training_ui(st.session_state.system, run_operation_sync)
    elif menu_option == "Получить прогнозы":
        show_prediction_ui(st.session_state.system, run_operation_sync)
    elif menu_option == "Добавить группу":
        show_data_ui(st.session_state.system, run_operation_sync)

if __name__ == "__main__":
    main()
