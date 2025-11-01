# [file name]: app.py (ИСПРАВЛЕННАЯ ВЕРСИЯ)
import sys
import os

# ⚡ ПРИНУДИТЕЛЬНО УСТАНАВЛИВАЕМ ПУТЬ К VENV
VENV_PATH = '/opt/project/env'
if os.path.exists(VENV_PATH):
    # Добавляем venv в путь
    sys.path.insert(0, os.path.join(VENV_PATH, 'lib/python3.12/site-packages'))
    # Устанавливаем правильный Python executable
    os.environ['PYTHONPATH'] = f"{VENV_PATH}/bin:{os.environ.get('PYTHONPATH', '')}"
    
    # Проверяем доступность torch
    try:
        import torch
        print(f"✅ PyTorch загружен: {torch.__version__}")
    except ImportError as e:
        print(f"❌ PyTorch ошибка: {e}")
        # Пытаемся добавить site-packages вручную
        site_packages = os.path.join(VENV_PATH, 'lib/python3.12/site-packages')
        if site_packages not in sys.path:
            sys.path.insert(0, site_packages)

# Остальные импорты
import streamlit as st
import logging
import threading
import time
import uuid
from datetime import datetime

# Настройка логирования
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger('SequencePredictorWeb')

# Добавляем пути
project_path = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, project_path)
sys.path.insert(0, os.path.join(project_path, 'model'))

st.set_page_config(page_title="AI Прогноз Последовательностей", page_icon="🔢", layout="wide")

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
    """Инициализация системы"""
    if st.session_state.system_initialized and st.session_state.system:
        return True
        
    try:
        logger.info("Инициализация AI системы...")
        from simple_system import SimpleNeuralSystem
        st.session_state.system = SimpleNeuralSystem()
        st.session_state.system.set_progress_callback(progress_callback)
        st.session_state.system_initialized = True
        logger.info("✅ Система AI успешно инициализирована")
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

def run_operation(operation_type, **kwargs):
    """Запуск операции в отдельном потоке"""
    try:
        if operation_type == "training":
            logger.info("🎯 Запуск обучения")
            result = st.session_state.system.train(epochs=15)
            logger.info("✅ Обучение успешно завершено")
            
        elif operation_type == "prediction":
            logger.info("🎯 Запуск прогнозирования")
            result = st.session_state.system.predict(top_k=8)
            logger.info(f"✅ Прогнозирование завершено, получено {len(result) if result else 0} прогнозов")
            
        elif operation_type == "add_data":
            sequence_input = kwargs.get('sequence_input', '')
            logger.info("🎯 Запуск добавления данных")
            result = st.session_state.system.add_data_and_retrain(sequence_input, retrain_epochs=3)
            logger.info(f"✅ Добавление данных завершено, получено {len(result) if result else 0} прогнозов")
            
        else:
            raise ValueError(f"Неизвестный тип операции: {operation_type}")
        
        st.session_state.operation_result = result
        st.session_state.operation_error = None
        
    except Exception as e:
        logger.error(f"❌ Ошибка в операции {operation_type}: {e}")
        st.session_state.operation_result = None
        st.session_state.operation_error = str(e)
    
    finally:
        st.session_state.operation_running = False

def show_progress_ui(operation_name, timeout_seconds=1200):
    """Показ UI прогресса"""
    progress_placeholder = st.empty()
    messages_placeholder = st.empty()
    
    start_time = time.time()
    operation_id = f"{operation_name}_{int(time.time())}"
    
    # Очищаем предыдущие сообщения
    st.session_state.progress_messages.clear()
    
    with progress_placeholder.container():
        st.info(f"🔄 Запущена операция: {operation_name}")
        progress_bar = st.progress(0)
        status_text = st.empty()
        time_text = st.empty()
        
        # Обновляем UI пока операция выполняется
        while st.session_state.operation_running:
            elapsed = time.time() - start_time
            if elapsed > timeout_seconds:
                status_text.error("⏰ Таймаут операции!")
                st.session_state.operation_error = f"Таймаут операции ({timeout_seconds} сек.)"
                st.session_state.operation_running = False
                break
            
            # Обновляем прогресс
            progress_percent = min(95, int((elapsed / timeout_seconds) * 100))
            progress_bar.progress(progress_percent)
            
            # Показываем сообщения
            if st.session_state.progress_messages:
                recent_messages = st.session_state.progress_messages[-5:]
                messages_placeholder.text_area(
                    "📝 Ход выполнения:", 
                    "\n".join(recent_messages), 
                    height=150
                )
            
            # Динамический статус
            if elapsed < 60:
                status_text.info("⏳ Инициализация процесса...")
            elif elapsed < 180:
                status_text.info("🔍 Анализ данных...")
            elif elapsed < 300:
                status_text.info("🧠 Обучение модели...")
            else:
                status_text.info("🎯 Финальная стадия...")
            
            time_text.text(f"⏱️ Прошло: {int(elapsed)} сек.")
            time.sleep(1)
        
        # Завершаем прогресс-бар
        if not st.session_state.operation_running:
            progress_bar.progress(100)
            if st.session_state.operation_error:
                status_text.error(f"❌ {st.session_state.operation_error}")
            else:
                status_text.success("✅ Операция завершена!")
                time_text.text(f"⏱️ Общее время: {int(time.time() - start_time)} сек.")

def show_status():
    """Показать статус системы"""
    st.sidebar.header("📊 Статус системы")
    
    if st.session_state.system_initialized and st.session_state.system:
        try:
            status = st.session_state.system.get_status()
            
            if status['is_trained']:
                st.sidebar.success("✅ Модель обучена")
            else:
                st.sidebar.warning("⚠️ Модель не обучена")
            
            st.sidebar.info(f"📁 Групп в датасете: {status['dataset_size']}")
            
            if status['has_sufficient_data']:
                st.sidebar.success("✅ Данных достаточно")
            else:
                st.sidebar.warning(f"⚠️ Нужно больше данных (минимум 50, сейчас {status['dataset_size']})")
            
            # Показываем последнюю группу
            try:
                from data_loader import load_dataset
                dataset = load_dataset()
                if dataset:
                    last_group = dataset[-1]
                    st.sidebar.info(f"📋 Последняя группа: {last_group}")
            except:
                pass
                
        except Exception as e:
            st.sidebar.error(f"Ошибка статуса: {e}")
    else:
        st.sidebar.error("❌ Система не инициализирована")

def show_advanced_controls():
    """Показать расширенные контролы"""
    st.sidebar.header("🔧 Управление")
    
    if st.sidebar.button("🔄 Обновить статус"):
        st.rerun()
    
    if st.sidebar.button("📊 Подробный статус"):
        try:
            if st.session_state.system:
                status = st.session_state.system.get_status()
                st.sidebar.json(status, expanded=False)
        except Exception as e:
            st.sidebar.error(f"Ошибка: {e}")

def train_model():
    """Обучить модель"""
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
        if not st.session_state.system_initialized:
            st.error("❌ Система не инициализирована")
            return
            
        # Запускаем операцию в отдельном потоке
        st.session_state.operation_running = True
        thread = threading.Thread(target=run_operation, args=("training",))
        thread.daemon = True
        thread.start()
        
        # Показываем прогресс
        show_progress_ui("обучение", timeout_seconds=1200)
        
        # Показываем результат
        if st.session_state.operation_error:
            st.error(f"❌ Ошибка обучения: {st.session_state.operation_error}")
        elif st.session_state.operation_result:
            st.balloons()
            st.success("🎉 Обучение успешно завершено!")
            
            st.subheader("🎯 Первые прогнозы после обучения")
            for i, (group, score) in enumerate(st.session_state.operation_result[:6], 1):
                confidence = "🟢 ВЫСОКАЯ" if score > 0.01 else "🟡 СРЕДНЯЯ" if score > 0.001 else "🔴 НИЗКАЯ"
                st.write(f"**{i}.** `{group[0]} {group[1]} {group[2]} {group[3]}`")
                st.write(f"   Уверенность: `{score:.6f}` {confidence}")
            
            # Сохраняем прогнозы
            try:
                from data_loader import save_predictions
                save_predictions(st.session_state.operation_result)
                st.info("💾 Прогнозы сохранены в кэш")
            except Exception as e:
                st.warning(f"⚠️ Не удалось сохранить прогнозы: {e}")
        else:
            st.warning("⚠️ Обучение завершено, но прогнозы не получены")

def make_prediction():
    """Сделать прогноз"""
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
        if not st.session_state.system_initialized:
            st.error("❌ Система не инициализирована")
            return
            
        # Проверяем что модель обучена
        status = st.session_state.system.get_status()
        if not status['is_trained']:
            st.error("❌ Модель не обучена! Сначала выполните обучение.")
            return
        
        # Запускаем операцию в отдельном потоке
        st.session_state.operation_running = True
        thread = threading.Thread(target=run_operation, args=("prediction",))
        thread.daemon = True
        thread.start()
        
        # Показываем прогресс
        show_progress_ui("прогнозирование", timeout_seconds=300)
        
        # Показываем результат
        if st.session_state.operation_error:
            st.error(f"❌ Ошибка прогнозирования: {st.session_state.operation_error}")
        elif st.session_state.operation_result:
            st.success(f"✅ Сгенерировано {len(st.session_state.operation_result)} прогнозов")
            
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
                from data_loader import save_predictions
                save_predictions(st.session_state.operation_result)
                st.info("💾 Прогнозы сохранены для сравнения")
            except Exception as e:
                st.warning(f"⚠️ Не удалось сохранить прогнозы: {e}")
        else:
            st.warning("⚠️ Прогнозы не сгенерированы")

def add_sequence():
    """Добавить новую последовательность"""
    st.header("➕ Добавить новую группу")
    
    # Показываем последнюю группу
    try:
        from data_loader import load_dataset
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
        if not st.session_state.system_initialized:
            st.error("❌ Система не инициализирована")
            return
            
        if not sequence_input:
            st.error("❌ Введите последовательность")
            return
            
        try:
            from data_loader import validate_group, compare_groups, load_predictions
            
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
            
            # Запускаем операцию в отдельном потоке
            st.session_state.operation_running = True
            thread = threading.Thread(target=run_operation, args=("add_data",), kwargs={'sequence_input': sequence_input})
            thread.daemon = True
            thread.start()
            
            # Показываем прогресс
            show_progress_ui("добавление данных", timeout_seconds=420)
            
            # Показываем результат
            if st.session_state.operation_error:
                st.error(f"❌ Ошибка при обработке: {st.session_state.operation_error}")
            elif st.session_state.operation_result:
                st.balloons()
                st.success("🎉 Группа добавлена и модель дообучена!")
                
                # Сохраняем прогнозы
                try:
                    from data_loader import save_predictions
                    save_predictions(st.session_state.operation_result)
                    st.info("💾 Новые прогнозы сохранены в кэш")
                except Exception as e:
                    st.warning(f"⚠️ Не удалось сохранить прогнозы: {e}")
                
                # Показываем новые прогнозы
                st.subheader("🎯 Обновленные прогнозы")
                for i, (group, score) in enumerate(st.session_state.operation_result[:8], 1):
                    confidence = "🟢 ВЫСОКАЯ" if score > 0.01 else "🟡 СРЕДНЯЯ" if score > 0.001 else "🔴 НИЗКАЯ"
                    st.write(f"**{i}.** `{group[0]} {group[1]} {group[2]} {group[3]}`")
                    st.write(f"   Уверенность: `{score:.6f}` {confidence}")
            else:
                st.warning("⚠️ Обработка завершена, но новые прогнозы не получены")
                
        except Exception as e:
            st.error(f"❌ Ошибка: {e}")

def main():
    st.title("🔢 AI Прогноз Числовых Последовательностей")
    st.markdown("Продвинутая нейросеть для анализа и прогнозирования числовых последовательностей с **системой самообучения**")
    
    # Инициализация системы
    if not st.session_state.system_initialized:
        with st.spinner("🔄 Инициализация AI системы..."):
            init_system()
    
    # Боковая панель с меню
    show_status()
    show_advanced_controls()
    
    st.sidebar.markdown("---")
    st.sidebar.header("🧭 Навигация")
    
    menu_option = st.sidebar.selectbox(
        "Выберите действие:",
        ["Обзор данных", "Обучить модель", "Получить прогнозы", "Добавить группу"]
    )
    
    # Основной контент
    if menu_option == "Обзор данных":
        st.header("📊 Обзор данных и аналитика")
        st.info("📈 Раздел в разработке... Сначала обучите модель и получите прогнозы")
        
    elif menu_option == "Обучить модель":
        train_model()
    elif menu_option == "Получить прогнозы":
        make_prediction()
    elif menu_option == "Добавить группу":
        add_sequence()

if __name__ == "__main__":
    main()