# [file name]: app.py (ИСПРАВЛЕННАЯ ВЕРСИЯ - КЛЮЧЕВЫЕ ИЗМЕНЕНИЯ)
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
            logger.info("✅ Система AI успешно инициализирована")
            return True
        except Exception as e:
            logger.error(f"❌ Ошибка инициализации системы: {e}")
            return False
    
    def _progress_callback(self, message):
        """Callback для отображения прогресса"""
        self.progress_messages.append(f"{datetime.now().strftime('%H:%M:%S')} - {message}")
        logger.info(f"📢 {message}")
    
    def _run_training_thread(self):
        """Запуск обучения в отдельном потоке"""
        try:
            self.thread_result = self.system.train(epochs=20)
            self.thread_error = None
        except Exception as e:
            self.thread_result = None
            self.thread_error = str(e)
            logger.error(f"❌ Ошибка в потоке обучения: {e}")
        finally:
            self.thread_complete = True
    
    def _run_prediction_thread(self):
        """Запуск прогнозирования в отдельном потоке"""
        try:
            self.thread_result = self.system.predict()
            self.thread_error = None
        except Exception as e:
            self.thread_result = None
            self.thread_error = str(e)
            logger.error(f"❌ Ошибка в потоке прогнозирования: {e}")
        finally:
            self.thread_complete = True
    
    def _run_add_data_thread(self, sequence_input):
        """Запуск добавления данных в отдельном потоке"""
        try:
            self.thread_result = self.system.add_data_and_retrain(sequence_input)
            self.thread_error = None
        except Exception as e:
            self.thread_result = None
            self.thread_error = str(e)
            logger.error(f"❌ Ошибка в потоке добавления данных: {e}")
        finally:
            self.thread_complete = True
    
    def show_progress_with_timeout(self, operation_name, timeout_seconds=600):
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
        elif operation_name == "prediction":
            thread = threading.Thread(target=self._run_prediction_thread)
        elif operation_name == "add_data":
            thread = threading.Thread(target=lambda: self._run_add_data_thread(st.session_state.get('current_sequence', '')))
        else:
            st.error("Неизвестная операция")
            return None
        
        thread.daemon = True
        thread.start()
        
        start_time = time.time()
        
        # Отображаем прогресс
        with progress_placeholder.container():
            st.info(f"🔄 Запущена операция: {operation_name}")
            progress_bar = st.progress(0)
            status_text = st.empty()
            time_text = st.empty()
            
            # Обновляем интерфейс пока поток работает
            while thread.is_alive():
                elapsed = time.time() - start_time
                if elapsed > timeout_seconds:
                    status_text.error("⏰ Таймаут операции!")
                    self.thread_error = "Таймаут операции"
                    break
                
                # Обновляем прогресс
                progress_percent = min(95, int((elapsed / timeout_seconds) * 100))
                progress_bar.progress(progress_percent)
                
                # Показываем последние сообщения
                if self.progress_messages:
                    recent_messages = self.progress_messages[-3:]  # Последние 3 сообщения
                    status_text.text("\n".join(recent_messages))
                
                time_text.text(f"⏱️ Прошло: {int(elapsed)} сек.")
                time.sleep(0.5)
            
            # Завершаем прогресс-бар
            if self.thread_complete and not self.thread_error:
                progress_bar.progress(100)
                status_text.success("✅ Операция завершена!")
            elif self.thread_error:
                progress_bar.progress(100)
                status_text.error(f"❌ Ошибка: {self.thread_error}")
        
        # Ждем завершения потока
        thread.join(timeout=5)
        
        return self.thread_result
    
    def show_status(self):
        """Показать статус системы"""
        st.sidebar.header("Статус системы")
        
        if self.system:
            try:
                status = self.system.get_status()
                st.sidebar.success("✅ Система AI: Активна")
                st.sidebar.info(f"Модель обучена: {'Да' if status['is_trained'] else 'Нет'}")
                st.sidebar.info(f"Размер датасета: {status['dataset_size']}")
                
                # Показываем статистику самообучения
                learning_stats = status.get('learning_stats', {})
                if isinstance(learning_stats, dict) and 'recent_accuracy_avg' in learning_stats:
                    accuracy = learning_stats['recent_accuracy_avg']
                    st.sidebar.info(f"📊 Средняя точность: {accuracy:.1%}")
                
                # Показываем последнюю группу из датасета
                try:
                    from data_loader import load_dataset
                    dataset = load_dataset()
                    if dataset:
                        last_group = dataset[-1] if dataset else "Нет данных"
                        st.sidebar.info(f"Последняя группа: {last_group}")
                except Exception as e:
                    st.sidebar.warning(f"Не удалось загрузить данные: {e}")
                
            except Exception as e:
                st.sidebar.error(f"Ошибка получения статуса: {e}")
        else:
            st.sidebar.error("❌ Система AI: Не инициализирована")
    
    def show_advanced_controls(self):
        """Показать расширенные контролы"""
        st.sidebar.header("🔧 Расширенные настройки")
        
        if st.sidebar.button("🔄 Обновить ансамблевую систему"):
            try:
                if hasattr(self.system, '_update_full_ensemble'):
                    self.system._update_full_ensemble()
                    st.sidebar.success("✅ Ансамблевая система обновлена!")
                else:
                    st.sidebar.warning("⚠️  Метод обновления ансамбля не доступен")
            except Exception as e:
                st.sidebar.error(f"❌ Ошибка: {e}")
        
        # Переключение ансамблевого режима
        if hasattr(self.system, 'ensemble_enabled'):
            current_mode = getattr(self.system, 'ensemble_enabled', True)
            new_mode = st.sidebar.checkbox("Использовать ансамблевый режим", value=current_mode)
            if new_mode != current_mode:
                try:
                    self.system.toggle_ensemble(new_mode)
                    st.sidebar.success(f"🔧 Ансамблевый режим {'включен' if new_mode else 'выключен'}")
                except Exception as e:
                    st.sidebar.error(f"❌ Ошибка переключения режима: {e}")
        
        # Кнопка сброса данных самообучения
        if st.sidebar.button("🗑️ Сбросить данные самообучения"):
            try:
                if hasattr(self.system, 'reset_learning_data'):
                    self.system.reset_learning_data()
                    st.sidebar.success("✅ Данные самообучения сброшены!")
                else:
                    st.sidebar.warning("⚠️  Метод сброса данных не доступен")
            except Exception as e:
                st.sidebar.error(f"❌ Ошибка: {e}")

    def show_learning_analytics(self):
        """Показать аналитику самообучения"""
        st.header("📈 Аналитика самообучения")
        
        try:
            if hasattr(self.system, 'get_learning_insights'):
                insights = self.system.get_learning_insights()
                
                if isinstance(insights, dict):
                    if 'message' in insights:
                        st.info(insights['message'])
                    else:
                        # Показываем метрики
                        col1, col2, col3 = st.columns(3)
                        
                        with col1:
                            st.metric(
                                "Проанализировано предсказаний",
                                insights.get('total_predictions_analyzed', 0)
                            )
                        
                        with col2:
                            accuracy = insights.get('recent_accuracy_avg', 0)
                            st.metric(
                                "Средняя точность",
                                f"{accuracy:.1%}"
                            )
                        
                        with col3:
                            best_acc = insights.get('best_accuracy', 0)
                            st.metric(
                                "Лучшая точность",
                                f"{best_acc:.1%}"
                            )
                        
                        # Рекомендации
                        recommendations = insights.get('recommendations', [])
                        if recommendations:
                            st.subheader("💡 Рекомендации по улучшению")
                            for rec in recommendations:
                                st.write(f"• {rec}")
                        else:
                            st.info("📊 Собираем данные для анализа...")
                else:
                    st.warning("Нет данных аналитики")
            else:
                st.warning("⚠️  Система самообучения не доступна")
                
        except Exception as e:
            st.error(f"Ошибка загрузки аналитики: {e}")

    def show_sequences(self):
        """Показать последние последовательности"""
        st.header("📊 Обзор данных")
        
        # Показываем аналитику самообучения
        self.show_learning_analytics()
        st.markdown("---")
        
        # Показываем последние прогнозы из кэша
        try:
            from data_loader import load_predictions
            predictions = load_predictions()
            if predictions:
                st.subheader("🎯 Сохраненные прогнозы из кэша")
                cols = st.columns(2)
                for i, (group, score) in enumerate(predictions[:4], 1):
                    with cols[(i-1) % 2]:
                        confidence = "🟢 Высокая" if score > 0.01 else "🟡 Средняя" if score > 0.001 else "🔴 Низкая"
                        st.metric(
                            f"Прогноз {i}",
                            f"{group[0]} {group[1]} {group[2]} {group[3]}",
                            f"Уверенность: {score:.6f}"
                        )
            else:
                st.info("📝 Нет сохраненных прогнозов в кэше")
        except Exception as e:
            st.error(f"Ошибка загрузки прогнозов: {e}")
        
        # Показываем последние группы
        try:
            from data_loader import load_dataset
            dataset = load_dataset()
            
            if dataset:
                st.success(f"Всего последовательностей: {len(dataset)}")
                
                # Показываем последние 5
                st.subheader("Последние 5 последовательностей:")
                for i, seq in enumerate(dataset[-5:], 1):
                    st.text_area(f"Последовательность {len(dataset)-5+i}", seq, height=60, key=f"seq_{i}")
            else:
                st.warning("Нет данных в датасете")
                
        except Exception as e:
            st.error(f"Ошибка загрузки данных: {e}")

    def _run_in_thread(self, func, *args, **kwargs):
        """Запуск функции в отдельном потоке"""
        import threading
        
        def wrapper():
            try:
                self.result = func(*args, **kwargs)
                self.thread_success = True
            except Exception as e:
                self.thread_error = e
                self.thread_success = False
        
        self.thread_success = None
        self.thread_error = None
        self.result = None
        
        thread = threading.Thread(target=wrapper)
        thread.daemon = True
        thread.start()
        
        return thread

    def train_model(self):
        """Обучить модель"""
        st.header("🧠 Обучить модель AI")
        st.info("Полное обучение модели на всех данных")
        
        if st.button("Начать обучение", type="primary", key="train_model_btn"):
            with st.spinner("Запуск обучения..."):
                result = self.show_progress_with_timeout("training", timeout_seconds=600)  # 10 минут
            
            if self.thread_error:
                st.error(f"❌ Ошибка обучения: {self.thread_error}")
            elif result:
                st.success("✅ Обучение завершено!")
                st.subheader("Результаты обучения")
                for i, (group, score) in enumerate(result, 1):
                    confidence = "🟢 Высокая" if score > 0.01 else "🟡 Средняя" if score > 0.001 else "🔴 Низкая"
                    st.write(f"{i}. `{group[0]} {group[1]} {group[2]} {group[3]}` (уверенность: {score:.6f}) {confidence}")
                
                # Сохраняем прогнозы
                try:
                    from data_loader import save_predictions
                    save_predictions(result)
                    st.info("💾 Прогнозы сохранены в кэш")
                except Exception as e:
                    st.warning(f"⚠️ Не удалось сохранить прогнозы: {e}")
            else:
                st.warning("⚠️ Обучение завершено, но прогнозы не получены")

    def make_prediction(self):
        """Сделать прогноз"""
        st.header("🔮 Получить прогнозы")
        st.info("AI проанализирует паттерны и сгенерирует прогнозы")
        
        if st.button("Сгенерировать прогнозы", type="primary", key="predict_btn"):
            with st.spinner("Запуск прогнозирования..."):
                result = self.show_progress_with_timeout("prediction", timeout_seconds=300)  # 5 минут
            
            if self.thread_error:
                st.error(f"❌ Ошибка прогнозирования: {self.thread_error}")
            elif result:
                st.success(f"✅ Сгенерировано {len(result)} прогнозов")
                st.subheader("Топ прогнозы:")
                
                cols = st.columns(2)
                for i, (group, score) in enumerate(result):
                    with cols[i % 2]:
                        confidence = "🟢 Высокая" if score > 0.01 else "🟡 Средняя" if score > 0.001 else "🔴 Низкая"
                        st.metric(
                            f"Прогноз {i+1}",
                            f"{group[0]} {group[1]} {group[2]} {group[3]}",
                            f"Уверенность: {score:.4f}"
                        )
                
                # Сохраняем прогнозы
                try:
                    from data_loader import save_predictions
                    save_predictions(result)
                    st.info("💾 Прогнозы сохранены в кэш")
                except Exception as e:
                    st.warning(f"⚠️ Не удалось сохранить прогнозы: {e}")
            else:
                st.warning("⚠️ Прогнозы не сгенерированы")

    def add_sequence(self):
        """Добавить новую последовательность"""
        st.header("➕ Добавить новую последовательность")
        
        # Показываем последнюю группу
        try:
            from data_loader import load_dataset
            dataset = load_dataset()
            if dataset:
                st.info(f"📋 Последняя добавленная группа: **{dataset[-1]}**")
        except:
            pass
        
        st.info("Введите 4 числа от 1 до 26 через пробел (например: '1 9 22 19')")
        
        sequence_input = st.text_input("Числовая последовательность:", placeholder="1 2 3 4", key="sequence_input")
        
        if st.button("Добавить последовательность и дообучить", type="primary", key="add_sequence_btn"):
            if not sequence_input:
                st.error("❌ Введите последовательность")
                return
                
            try:
                from data_loader import validate_group, compare_groups, load_predictions
                
                if not validate_group(sequence_input):
                    st.error("❌ Неверный формат последовательности. Должно быть 4 числа 1-26 через пробел")
                    return
                
                # Сохраняем последовательность в session state
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
                            st.write(f"  {i}) Прогноз: {pred_group[0]} {pred_group[1]} {pred_group[2]} {pred_group[3]}")
                            st.write(f"     Совпадения по парам: {comparison['total_matches']}/4")
                            st.write(f"     Точные совпадения: {comparison['exact_matches']}/4")
                    else:
                        st.info("📝 Совпадений с предыдущими прогнозами нет")
                else:
                    st.info("📝 Нет предыдущих прогнозов для сравнения")
                
                # Запускаем добавление данных
                with st.spinner("Запуск обработки данных..."):
                    result = self.show_progress_with_timeout("add_data", timeout_seconds=300)  # 5 минут
                
                if self.thread_error:
                    st.error(f"❌ Ошибка при обработке: {self.thread_error}")
                elif result:
                    st.success("✅ Последовательность добавлена и модель дообучена!")
                    
                    # Сохраняем прогнозы
                    try:
                        from data_loader import save_predictions
                        save_predictions(result)
                        st.info("💾 Новые прогнозы сохранены в кэш")
                    except Exception as e:
                        st.warning(f"⚠️ Не удалось сохранить прогнозы: {e}")
                    
                    # Показываем новые прогнозы
                    st.subheader("🎯 Новые прогнозы после дообучения")
                    for i, (group, score) in enumerate(result, 1):
                        confidence = "🟢 Высокая" if score > 0.01 else "🟡 Средняя" if score > 0.001 else "🔴 Низкая"
                        st.write(f"{i}. `{group[0]} {group[1]} {group[2]} {group[3]}` (уверенность: {score:.6f}) {confidence}")
                else:
                    st.warning("⚠️ Обработка завершена, но новые прогнозы не получены")
                    
            except Exception as e:
                st.error(f"❌ Ошибка: {e}")


def main():
    st.title("🔢 AI Прогноз Числовых Последовательностей")
    st.write("Продвинутая нейросеть для анализа и прогнозирования числовых последовательностей с системой самообучения")
    
    # Инициализация интерфейса
    interface = WebInterface()
    
    # Боковая панель с меню
    interface.show_status()
    interface.show_advanced_controls()
    
    st.sidebar.header("Навигация")
    menu_option = st.sidebar.selectbox(
        "Выберите действие:",
        ["Обзор данных", "Добавить последовательность", "Обучить модель", "Получить прогнозы"]
    )
    
    # Основной контент
    if menu_option == "Обзор данных":
        interface.show_sequences()
    elif menu_option == "Добавить последовательность":
        interface.add_sequence()
    elif menu_option == "Обучить модель":
        interface.train_model()
    elif menu_option == "Получить прогнозы":
        interface.make_prediction()

if __name__ == "__main__":
    main()