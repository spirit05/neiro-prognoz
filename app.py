# [file name]: app.py
#!/usr/bin/env python3
import sys
import os
import logging

# ⚡ ПРИНУДИТЕЛЬНО УСТАНАВЛИВАЕМ ПУТИ
PROJECT_PATH = '/opt/project'
sys.path.insert(0, PROJECT_PATH)
sys.path.insert(0, os.path.join(PROJECT_PATH, 'model'))

# ⚡ ПРИНУДИТЕЛЬНО ДОБАВЛЯЕМ VENV В ПУТЬ
VENV_PYTHON_PATH = '/opt/project/env/lib/python3.12/site-packages'
if os.path.exists(VENV_PYTHON_PATH) and VENV_PYTHON_PATH not in sys.path:
    sys.path.insert(0, VENV_PYTHON_PATH)

# ⚡ ТЕПЕРЬ ИМПОРТИРУЕМ НАШИ МОДУЛИ
try:
    from model.simple_system import SimpleNeuralSystem
    from model.data_loader import load_dataset, save_dataset, validate_group, compare_groups, save_predictions, load_predictions
    print("✅ Все импорты успешны")
except ImportError as e:
    print(f"❌ Ошибка импорта: {e}")
    print(f"🔍 sys.path: {sys.path}")

# Остальные импорты
import streamlit as st
import time
import uuid
from datetime import datetime

# Настройка логирования
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger('SequencePredictorWeb')

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
        from model.simple_system import SimpleNeuralSystem
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

def run_operation_sync(operation_type, **kwargs):
    """СИНХРОННЫЙ запуск операции (без потоков)"""
    try:
        # ⚡ ДОБАВЛЯЕМ ОТЛАДОЧНЫЙ ЛОГ
        debug_msg = f"🎯 DEBUG: Запуск операции {operation_type}"
        print(debug_msg)
        with open("/opt/project/debug_log.txt", "a", encoding="utf-8") as f:
            f.write(f"{datetime.now()} - Запуск операции {operation_type}\n")
        
        # Очищаем предыдущие сообщения
        st.session_state.progress_messages = []
        
        if operation_type == "training":
            logger.info("🎯 Запуск обучения")
            result = st.session_state.system.train(epochs=20)
            logger.info("✅ Обучение успешно завершено")
            
        elif operation_type == "prediction":
            logger.info("🎯 Запуск прогнозирования")
            result = st.session_state.system.predict(top_k=4)
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
        return result
        
    except Exception as e:
        logger.error(f"❌ Ошибка в операции {operation_type}: {e}")
        st.session_state.operation_result = None
        st.session_state.operation_error = str(e)
        return None

def show_progress_ui(operation_name):
    """Показ UI прогресса"""
    st.info(f"🔄 Выполняется операция: {operation_name}")
    
    # Показываем сообщения прогресса
    if st.session_state.progress_messages:
        recent_messages = st.session_state.progress_messages[-10:]
        st.text_area(
            "📝 Ход выполнения:", 
            "\n".join(recent_messages), 
            height=200
        )
    
    # Обновляем страницу для показа новых сообщений
    time.sleep(2)
    st.rerun()

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
            
        # Запускаем операцию СИНХРОННО
        with st.spinner("🔄 Запуск обучения..."):
            result = run_operation_sync("training")
        
        # Показываем результат
        if st.session_state.operation_error:
            st.error(f"❌ Ошибка обучения: {st.session_state.operation_error}")
        elif st.session_state.operation_result:
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
        
        # Запускаем операцию СИНХРОННО
        with st.spinner("🔄 Генерация прогнозов..."):
            result = run_operation_sync("prediction")
        
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
            
            # Запускаем операцию СИНХРОННО
            with st.spinner("🔄 Обработка данных..."):
                result = run_operation_sync("add_data", sequence_input=sequence_input)
            
            # Показываем результат
            if st.session_state.operation_error:
                st.error(f"❌ Ошибка при обработке: {st.session_state.operation_error}")
            elif st.session_state.operation_result:
                st.balloons()
                st.success("🎉 Группа добавлена и модель дообучена!")
                
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

def show_data_overview():
    """Показать обзор данных и аналитику"""
    st.header("📊 Обзор данных и аналитика")
    
    if not st.session_state.system_initialized:
        st.error("❌ Система не инициализирована")
        return
    
    try:
        # Статус системы
        status = st.session_state.system.get_status()
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.subheader("🧠 Статус модели")
            if status['is_trained']:
                st.success("✅ Модель обучена")
            else:
                st.warning("⚠️ Модель не обучена")
            
            st.info(f"📁 Групп в датасете: {status['dataset_size']}")
            
            if status['has_sufficient_data']:
                st.success("✅ Данных достаточно")
            else:
                st.warning(f"⚠️ Нужно больше данных (минимум 50)")
        
        with col2:
            st.subheader("🔧 Система")
            st.info(f"🎯 Тип модели: {status.get('model_type', 'УСИЛЕННАЯ')}")
            
            ensemble_info = status.get('ensemble_info', {})
            if ensemble_info.get('ensemble_enabled', False):
                st.success("✅ Ансамблевый режим включен")
            else:
                st.info("🔧 Ансамблевый режим выключен")
        
        # Последние прогнозы
        st.subheader("🎯 Последние прогнозы")
        predictions = load_predictions()
        if predictions:
            for i, (group, score) in enumerate(predictions[:4], 1):
                confidence = "🟢 ВЫСОКАЯ" if score > 0.01 else "🟡 СРЕДНЯЯ" if score > 0.001 else "🔴 НИЗКАЯ"
                st.write(f"**{i}.** `{group[0]} {group[1]} {group[2]} {group[3]}` - уверенность: `{score:.6f}` {confidence}")
        else:
            st.info("📝 Прогнозы еще не сгенерированы")
        
        # Аналитика самообучения
        st.subheader("📈 Аналитика самообучения")
        learning_stats = st.session_state.system.get_learning_insights()
        
        if 'message' in learning_stats:
            st.info(learning_stats['message'])
        else:
            col1, col2 = st.columns(2)
            with col1:
                if 'recent_accuracy_avg' in learning_stats:
                    accuracy = learning_stats['recent_accuracy_avg']
                    st.metric("🎯 Средняя точность", f"{accuracy:.1%}")
                if 'total_predictions_analyzed' in learning_stats:
                    st.metric("📊 Проанализировано прогнозов", learning_stats['total_predictions_analyzed'])
            
            with col2:
                if 'best_accuracy' in learning_stats:
                    best = learning_stats['best_accuracy']
                    st.metric("🏆 Лучшая точность", f"{best:.1%}")
                if 'worst_accuracy' in learning_stats:
                    worst = learning_stats['worst_accuracy']
                    st.metric("📉 Худшая точность", f"{worst:.1%}")
            
            # Рекомендации
            if 'recommendations' in learning_stats and learning_stats['recommendations']:
                st.subheader("💡 Рекомендации")
                for rec in learning_stats['recommendations']:
                    st.write(f"• {rec}")
        
    except Exception as e:
        st.error(f"❌ Ошибка загрузки данных: {e}")

def main():
    st.title("🔢 AI Прогноз Числовых Последовательностей")
    st.markdown("Продвинутая нейросеть для анализа и прогнозирования числовых последовательностей с **системой самообучения**")
    
    # Инициализация системы
    if not st.session_state.system_initialized:
        with st.spinner("🔄 Инициализация AI системы..."):
            init_system()

    # Боковая панель с меню
    show_status()
    
    st.sidebar.markdown("---")
    st.sidebar.header("🧭 Навигация")
    
    menu_option = st.sidebar.selectbox(
        "Выберите действие:",
        ["Обзор данных", "Обучить модель", "Получить прогнозы", "Добавить группу"]
    )
    
    # Основной контент
    if menu_option == "Обзор данных":
        show_data_overview() 
    elif menu_option == "Обучить модель":
        train_model()
    elif menu_option == "Получить прогнозы":
        make_prediction()
    elif menu_option == "Добавить группу":
        add_sequence()

if __name__ == "__main__":
    main()
