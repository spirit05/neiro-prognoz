# [file name]: app.py (ОПТИМИЗИРОВАННАЯ ВЕРСИЯ)
import streamlit as st
import sys
import os
import logging
import threading
import time
from datetime import datetime

# Настройка логирования
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger('SequencePredictorWeb')

# Добавляем пути
project_path = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, project_path)
sys.path.insert(0, os.path.join(project_path, 'model'))

st.set_page_config(page_title="AI Прогноз Последовательностей", page_icon="🔢", layout="wide")

class WebInterface:
    def __init__(self):
        self.system = None
        self._init_system()
        self.progress_messages = []
        self.thread_result = None
        self.thread_error = None
        self.thread_complete = False
    
    def _init_system(self):
        """Инициализация системы"""
        try:
            logger.info("Инициализация AI системы...")
            from simple_system import SimpleNeuralSystem
            self.system = SimpleNeuralSystem()
            self.system.set_progress_callback(self._progress_callback)
            logger.info("✅ Системa AI успешно инициализирована")
            
            # Проверяем статус системы
            status = self.system.get_status()
            st.sidebar.info(f"📊 Датасет: {status['dataset_size']} групп")
            st.sidebar.info(f"🧠 Модель обучена: {'✅ Да' if status['is_trained'] else '❌ Нет'}")
            
            return True
        except Exception as e:
            logger.error(f"❌ Ошибка инициализации системы: {e}")
            st.error(f"❌ Ошибка инициализации системы: {e}")
            return False
    
    def _progress_callback(self, message):
        """Callback для отображения прогресса"""
        timestamp = datetime.now().strftime('%H:%M:%S')
        formatted_message = f"{timestamp} - {message}"
        self.progress_messages.append(formatted_message)
        logger.info(f"📢 {message}")
    
    def _run_training_thread(self, epochs=15):  # Уменьшили эпохи для скорости
        """Запуск обучения в отдельном потоке"""
        try:
            logger.info(f"🎯 Запуск обучения на {epochs} эпох")
            self.thread_result = self.system.train(epochs=epochs)
            logger.info("✅ Обучение успешно завершено")
            self.thread_error = None
        except Exception as e:
            logger.error(f"❌ Ошибка в потоке обучения: {e}")
            self.thread_result = None
            self.thread_error = str(e)
        finally:
            self.thread_complete = True
    
    def _run_prediction_thread(self):
        """Запуск прогнозирования в отдельном потоке"""
        try:
            logger.info("🎯 Запуск прогнозирования")
            self.thread_result = self.system.predict(top_k=8)  # Уменьшили количество прогнозов
            logger.info(f"✅ Прогнозирование завершено, получено {len(self.thread_result) if self.thread_result else 0} прогнозов")
            self.thread_error = None
        except Exception as e:
            logger.error(f"❌ Ошибка в потоке прогнозирования: {e}")
            self.thread_result = None
            self.thread_error = str(e)
        finally:
            self.thread_complete = True
    
    def _run_add_data_thread(self, sequence_input):
        """Запуск добавления данных в отдельном потоке"""
        try:
            logger.info("🎯 Запуск добавления данных")
            self.thread_result = self.system.add_data_and_retrain(sequence_input, retrain_epochs=3)  # Меньше эпох для дообучения
            logger.info(f"✅ Добавление данных завершено, получено {len(self.thread_result) if self.thread_result else 0} прогнозов")
            self.thread_error = None
        except Exception as e:
            logger.error(f"❌ Ошибка в потоке добавления данных: {e}")
            self.thread_result = None
            self.thread_error = str(e)
        finally:
            self.thread_complete = True
    
    def show_progress_with_timeout(self, operation_name, timeout_seconds=1200):  # Увеличили до 20 минут
        """Показ прогресса с таймаутом"""
        progress_placeholder = st.empty()
        messages_placeholder = st.empty()
        
        # Сбрасываем состояние
        self.thread_result = None
        self.thread_error = None
        self.thread_complete = False
        self.progress_messages.clear()
        
        # Запускаем соответствующий поток
        if operation_name == "training":
            thread = threading.Thread(target=self._run_training_thread)
            estimated_time = "15-20 минут"
        elif operation_name == "prediction":
            thread = threading.Thread(target=self._run_prediction_thread)
            estimated_time = "2-5 минут"
        elif operation_name == "add_data":
            thread = threading.Thread(target=lambda: self._run_add_data_thread(st.session_state.get('current_sequence', '')))
            estimated_time = "3-7 минут"
        else:
            st.error("Неизвестная операция")
            return None
        
        thread.daemon = True
        thread.start()
        
        start_time = time.time()
        
        # Отображаем прогресс
        with progress_placeholder.container():
            st.info(f"🔄 Запущена операция: {operation_name} (ожидаемое время: {estimated_time})")
            progress_bar = st.progress(0)
            status_text = st.empty()
            time_text = st.empty()
            messages_text = st.empty()
            
            # Обновляем интерфейс пока поток работает
            while thread.is_alive():
                elapsed = time.time() - start_time
                if elapsed > timeout_seconds:
                    status_text.error("⏰ Таймаут операции! Процесс занимает слишком много времени.")
                    self.thread_error = f"Таймаут операции ({timeout_seconds} сек.)"
                    break
                
                # Обновляем прогресс на основе времени
                progress_percent = min(95, int((elapsed / timeout_seconds) * 100))
                progress_bar.progress(progress_percent)
                
                # Показываем последние сообщения
                if self.progress_messages:
                    recent_messages = self.progress_messages[-5:]  # Последние 5 сообщений
                    messages_text.text_area("📝 Ход выполнения:", "\n".join(recent_messages), height=150)
                
                # Динамический статус
                if elapsed < 60:
                    status_text.info("⏳ Инициализация процесса...")
                elif elapsed < 180:
                    status_text.info("🔍 Анализ данных...")
                elif elapsed < 300:
                    status_text.info("🧠 Обучение модели...")
                else:
                    status_text.info("🎯 Финальная стадия...")
                
                time_text.text(f"⏱️ Прошло: {int(elapsed)} сек. / Лимит: {timeout_seconds} сек.")
                time.sleep(1)  # Увеличили интервал обновления
            
            # Завершаем прогресс-бар
            if self.thread_complete and not self.thread_error:
                progress_bar.progress(100)
                status_text.success("✅ Операция завершена успешно!")
                time_text.text(f"⏱️ Общее время: {int(time.time() - start_time)} сек.")
            elif self.thread_error:
                progress_bar.progress(100)
                status_text.error(f"❌ {self.thread_error}")
        
        # Ждем завершения потока
        thread.join(timeout=10)
        
        return self.thread_result

    def show_status(self):
        """Показать статус системы"""
        st.sidebar.header("📊 Статус системы")
        
        if self.system:
            try:
                status = self.system.get_status()
                
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

    def show_advanced_controls(self):
        """Показать расширенные контролы"""
        st.sidebar.header("🔧 Управление")
        
        if st.sidebar.button("🔄 Обновить статус", key="refresh_status"):
            st.rerun()
        
        if st.sidebar.button("📊 Подробный статус", key="detailed_status"):
            try:
                status = self.system.get_status()
                st.sidebar.json(status, expanded=False)
            except Exception as e:
                st.sidebar.error(f"Ошибка: {e}")

    def train_model(self):
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
            Процесс продолжится в фоне.
            """)
        
        if st.button("🚀 Начать полное обучение", type="primary", key="train_full_btn"):
            with st.spinner("Подготовка к обучению..."):
                result = self.show_progress_with_timeout("training", timeout_seconds=1200)  # 20 минут
            
            if self.thread_error:
                st.error(f"❌ Ошибка обучения: {self.thread_error}")
                st.info("💡 Попробуйте запустить обучение через CLI интерфейс для более детального контроля")
            elif result:
                st.balloons()
                st.success("🎉 Обучение успешно завершено!")
                
                st.subheader("🎯 Первые прогнозы после обучения")
                for i, (group, score) in enumerate(result[:6], 1):  # Показываем только 6 лучших
                    confidence = "🟢 ВЫСОКАЯ" if score > 0.01 else "🟡 СРЕДНЯЯ" if score > 0.001 else "🔴 НИЗКАЯ"
                    st.write(f"**{i}.** `{group[0]} {group[1]} {group[2]} {group[3]}`")
                    st.write(f"   Уверенность: `{score:.6f}` {confidence}")
                    st.progress(min(1.0, score * 100))
                
                # Сохраняем прогнозы
                try:
                    from data_loader import save_predictions
                    save_predictions(result)
                    st.info("💾 Прогнозы сохранены в кэш для будущего сравнения")
                except Exception as e:
                    st.warning(f"⚠️ Не удалось сохранить прогнозы: {e}")
            else:
                st.warning("⚠️ Обучение завершено, но прогнозы не получены")

    def make_prediction(self):
        """Сделать прогноз"""
        st.header("🔮 Получить прогнозы")
        
        st.info("""
        **AI проанализирует паттерны и сгенерирует прогнозы:**
        - Использует обученную модель
        - Применяет ансамблевые методы
        - Учитывает исторические паттерны
        - **Время: 2-5 минут**
        """)
        
        if st.button("🎯 Сгенерировать прогнозы", type="primary", key="predict_btn"):
            # Проверяем что модель обучена
            status = self.system.get_status()
            if not status['is_trained']:
                st.error("❌ Модель не обучена! Сначала выполните обучение.")
                return
            
            with st.spinner("Запуск анализа..."):
                result = self.show_progress_with_timeout("prediction", timeout_seconds=300)  # 5 минут
            
            if self.thread_error:
                st.error(f"❌ Ошибка прогнозирования: {self.thread_error}")
            elif result:
                st.success(f"✅ Сгенерировано {len(result)} прогнозов")
                
                st.subheader("🏆 Топ прогнозы")
                cols = st.columns(2)
                
                for i, (group, score) in enumerate(result):
                    with cols[i % 2]:
                        confidence = "🟢 ВЫСОКАЯ" if score > 0.01 else "🟡 СРЕДНЯЯ" if score > 0.001 else "🔴 НИЗКАЯ"
                        
                        st.metric(
                            label=f"Прогноз #{i+1}",
                            value=f"{group[0]} {group[1]} {group[2]} {group[3]}",
                            delta=f"{score:.4f} {confidence}"
                        )
                
                # Сохраняем прогнозы
                try:
                    from data_loader import save_predictions
                    save_predictions(result)
                    st.info("💾 Прогнозы сохранены для сравнения с будущими результатами")
                except Exception as e:
                    st.warning(f"⚠️ Не удалось сохранить прогнозы: {e}")
            else:
                st.warning("⚠️ Прогнозы не сгенерированы")

    def add_sequence(self):
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
        
        sequence_input = st.text_input(
            "Числовая последовательность:",
            placeholder="1 9 22 19",
            key="sequence_input",
            help="Пример: 1 9 22 19 - 4 числа через пробел, от 1 до 26"
        )
        
        if st.button("✅ Добавить и дообучить", type="primary", key="add_sequence_btn"):
            if not sequence_input:
                st.error("❌ Введите последовательность")
                return
                
            try:
                from data_loader import validate_group, compare_groups, load_predictions
                
                if not validate_group(sequence_input):
                    st.error("❌ Неверный формат! Должно быть 4 числа 1-26 через пробел, числа в парах не должны совпадать")
                    return
                
                # Сохраняем последовательность
                st.session_state.current_sequence = sequence_input
                
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
                            st.write(f"   - Точные совпадения: **{comparison['exact_matches']}/4**")
                    else:
                        st.info("📝 Совпадений с предыдущими прогнозами нет")
                else:
                    st.info("📝 Нет предыдущих прогнозов для сравнения")
                
                st.markdown("---")
                
                # Запускаем добавление данных
                with st.spinner("Запуск обработки..."):
                    result = self.show_progress_with_timeout("add_data", timeout_seconds=420)  # 7 минут
                
                if self.thread_error:
                    st.error(f"❌ Ошибка при обработке: {self.thread_error}")
                elif result:
                    st.balloons()
                    st.success("🎉 Группа добавлена и модель дообучена!")
                    
                    # Сохраняем прогнозы
                    try:
                        from data_loader import save_predictions
                        save_predictions(result)
                        st.info("💾 Новые прогнозы сохранены в кэш")
                    except Exception as e:
                        st.warning(f"⚠️ Не удалось сохранить прогнозы: {e}")
                    
                    # Показываем новые прогнозы
                    st.subheader("🎯 Обновленные прогнозы")
                    for i, (group, score) in enumerate(result[:8], 1):  # Показываем 8 лучших
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
    
    # Инициализация интерфейса
    interface = WebInterface()
    
    # Боковая панель с меню
    interface.show_status()
    interface.show_advanced_controls()
    
    st.sidebar.markdown("---")
    st.sidebar.header("🧭 Навигация")
    
    menu_option = st.sidebar.selectbox(
        "Выберите действие:",
        ["Обзор данных", "Обучить модель", "Получить прогнозы", "Добавить группу"],
        key="main_menu"
    )
    
    # Основной контент
    if menu_option == "Обзор данных":
        st.header("📊 Обзор данных и аналитика")
        # Здесь можно добавить показ данных когда система стабильно заработает
        st.info("📈 Раздел в разработке... Сначала обучите модель и получите прогнозы")
        
    elif menu_option == "Обучить модель":
        interface.train_model()
    elif menu_option == "Получить прогнозы":
        interface.make_prediction()
    elif menu_option == "Добавить группу":
        interface.add_sequence()

if __name__ == "__main__":
    main()