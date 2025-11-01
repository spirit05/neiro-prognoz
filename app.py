# [file name]: app.py (ПОЛНОСТЬЮ ОБНОВЛЕННЫЙ)
import streamlit as st
import sys
import os
import json
import time

# Добавляем путь к модели
sys.path.append('model')

st.set_page_config(
    page_title="AI Прогноз Последовательностей",
    page_icon="🔢", 
    layout="wide"
)

class WebInterface:
    def __init__(self):
        self.system = None
        self._init_system()
    
    def _init_system(self):
        """Инициализация системы"""
        try:
            from simple_system import SimpleNeuralSystem
            self.system = SimpleNeuralSystem()
            return True
        except Exception as e:
            st.error(f"Ошибка инициализации системы: {e}")
            return False
    
    def show_status(self):
        """Показать статус системы"""
        st.sidebar.header("Статус системы")
        
        if self.system:
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
            except:
                pass
            
            # Показываем последние прогнозы
            try:
                from data_loader import load_predictions
                predictions = load_predictions()
                if predictions:
                    st.sidebar.info(f"Последние прогнозы: {len(predictions)}")
                    for i, (group, score) in enumerate(predictions[:2], 1):
                        st.sidebar.text(f"  {i}. {group[0]} {group[1]} {group[2]} {group[3]}")
            except:
                pass
        else:
            st.sidebar.error("❌ Система AI: Не инициализирована")
    
    def show_advanced_controls(self):
        """Показать расширенные контролы"""
        st.sidebar.header("🔧 Расширенные настройки")
        
        if st.sidebar.button("🔄 Обновить ансамблевую систему"):
            try:
                self.system._update_full_ensemble()
                st.sidebar.success("✅ Ансамблевая система обновлена!")
            except Exception as e:
                st.sidebar.error(f"❌ Ошибка: {e}")
        
        # Переключение ансамблевого режима
        current_mode = getattr(self.system, 'ensemble_enabled', True)
        new_mode = st.sidebar.checkbox("Использовать ансамблевый режим", value=current_mode)
        if new_mode != current_mode:
            self.system.toggle_ensemble(new_mode)
            st.sidebar.success(f"🔧 Ансамблевый режим {'включен' if new_mode else 'выключен'}")
        
        # Кнопка сброса данных самообучения
        if st.sidebar.button("🗑️ Сбросить данные самообучения"):
            try:
                self.system.reset_learning_data()
                st.sidebar.success("✅ Данные самообучения сброшены!")
            except Exception as e:
                st.sidebar.error(f"❌ Ошибка: {e}")
        
        # Информация о системе
        if st.sidebar.button("📊 Детальный статус"):
            status = self.system.get_status()
            st.sidebar.json(status)

    def show_learning_analytics(self):
        """Показать аналитику самообучения"""
        st.header("📈 Аналитика самообучения")
        
        try:
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
                from data_loader import validate_group, compare_groups, load_predictions, save_predictions
                
                if validate_group(sequence_input):
                    # === 1. СРАВНЕНИЕ С ПРЕДЫДУЩИМИ ПРОГНОЗАМИ ===
                    sequence_numbers = [int(x) for x in sequence_input.strip().split()]
                    sequence_tuple = tuple(sequence_numbers)
                    
                    previous_predictions = load_predictions()
                    
                    # Создаем контейнер для результатов сравнения (остается видимым)
                    comparison_container = st.container()
                    
                    with comparison_container:
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
                    
                    # Создаем контейнер для прогресса обучения
                    progress_container = st.empty()
                    dynamic_output = st.empty()
                    
                    # Лоадер сверху
                    with progress_container:
                        st.info("🔄 Добавляем данные и дообучаем модель...")
                    
                    # Callback для реального прогресса
                    def progress_callback(message):
                        dynamic_output.text(f"▶️ {message}")
                    
                    # Устанавливаем callback в систему
                    self.system.set_progress_callback(progress_callback)
                    
                    # === 2. РЕАЛЬНОЕ ДОБАВЛЕНИЕ И ОБУЧЕНИЕ ===
                    predictions = self.system.add_data_and_retrain(sequence_input)
                    
                    # === 3. СОХРАНЕНИЕ НОВЫХ ПРОГНОЗОВ ===
                    if predictions:
                        save_predictions(predictions)
                        dynamic_output.text("💾 Сохраняем новые прогнозы в кэш...")
                        time.sleep(1)  # Небольшая пауза чтобы увидеть сообщение
                    
                    # Очищаем анимацию прогресса
                    dynamic_output.empty()
                    progress_container.empty()
                    
                    st.success("✅ Последовательность добавлена и модель дообучена!")
                    
                    # === 4. ПОКАЗ НОВЫХ ПРОГНОЗОВ ===
                    if predictions:
                        st.subheader("🎯 Новые прогнозы после дообучения (сохранены в кэш)")
                        for i, (group, score) in enumerate(predictions, 1):
                            confidence = "🟢 Высокая" if score > 0.01 else "🟡 Средняя" if score > 0.001 else "🔴 Низкая"
                            st.write(f"{i}. `{group[0]} {group[1]} {group[2]} {group[3]}` (уверенность: {score:.6f}) {confidence}")
                        
                        st.info("💾 Эти прогнозы сохранены и будут использоваться для сравнения при следующем добавлении")
                    else:
                        st.warning("⚠️ Не удалось сгенерировать новые прогнозы")
                else:
                    st.error("❌ Неверный формат последовательности. Должно быть 4 числа 1-26 через пробел")
                    
            except Exception as e:
                st.error(f"Ошибка: {e}")
    
    def train_model(self):
        """Обучить модель"""
        st.header("🧠 Обучить модель AI")
        st.info("Полное обучение модели на всех данных")
        
        if st.button("Начать обучение", type="primary", key="train_model_btn"):
            try:
                # Создаем контейнер для прогресса
                progress_container = st.empty()
                dynamic_output = st.empty()
                
                # Лоадер сверху
                with progress_container:
                    st.info("🔄 Идет обучение модели...")
                
                # Callback для реального прогресса
                def progress_callback(message):
                    dynamic_output.text(f"▶️ {message}")
                
                # Устанавливаем callback в систему
                self.system.set_progress_callback(progress_callback)
                
                # Реальное обучение
                predictions = self.system.train(epochs=20)
                
                # Очищаем анимацию
                dynamic_output.empty()
                progress_container.empty()
                
                st.success("✅ Обучение завершено!")
                
                if predictions:
                    st.subheader("Результаты обучения")
                    for i, (group, score) in enumerate(predictions, 1):
                        confidence = "🟢 Высокая" if score > 0.01 else "🟡 Средняя" if score > 0.001 else "🔴 Низкая"
                        st.write(f"{i}. `{group[0]} {group[1]} {group[2]} {group[3]}` (уверенность: {score:.6f})")
                        
            except Exception as e:
                st.error(f"Ошибка обучения: {e}")
    
    def make_prediction(self):
        """Сделать прогноз"""
        st.header("🔮 Получить прогнозы")
        st.info("AI проанализирует паттерны и сгенерирует прогнозы")
        
        if st.button("Сгенерировать прогнозы", type="primary", key="predict_btn"):
            try:
                # Создаем контейнер для прогресса
                progress_container = st.empty()
                dynamic_output = st.empty()
                
                # Лоадер сверху
                with progress_container:
                    st.info("🔄 AI анализирует паттерны...")
                
                # Callback для реального прогресса
                def progress_callback(message):
                    dynamic_output.text(f"▶️ {message}")
                
                # Устанавливаем callback в систему
                self.system.set_progress_callback(progress_callback)
                
                # Реальное прогнозирование
                predictions = self.system.predict()
                
                # Очищаем анимацию
                dynamic_output.empty()
                progress_container.empty()
                
                if predictions:
                    st.success(f"✅ Сгенерировано {len(predictions)} прогнозов")
                    
                    st.subheader("Топ прогнозы:")
                    for i, (group, score) in enumerate(predictions, 1):
                        confidence = "🟢 Высокая" if score > 0.01 else "🟡 Средняя" if score > 0.001 else "🔴 Низкая"
                        st.metric(
                            f"Прогноз {i}",
                            f"{group[0]} {group[1]} {group[2]} {group[3]}",
                            f"Уверенность: {confidence}"
                        )
                    
                    # Сохраняем прогнозы в кэш
                    from data_loader import save_predictions
                    save_predictions(predictions)
                    st.info("💾 Прогнозы сохранены в кэш")
                else:
                    st.warning("⚠️ Нет доступных прогнозов")
                    
            except Exception as e:
                st.error(f"Ошибка прогнозирования: {e}")

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