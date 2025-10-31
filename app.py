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
            st.sidebar.error("❌ Системa AI: Не инициализирована")
    
    def show_sequences(self):
        """Показать последние последовательности"""
        st.header("📊 Обзор данных")
        
        # Показываем последние прогнозы
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
        except Exception as e:
            st.error(f"Ошибка загрузки прогнозов: {e}")
        
        try:
            from data_loader import load_dataset
            dataset = load_dataset()
            
            if dataset:
                st.success(f"Всего последовательностей: {len(dataset)}")
                
                # Показываем последние 5
                st.subheader("Последние 5 последовательностей:")
                for i, seq in enumerate(dataset[-5:], 1):
                    st.text_area(f"Последовательность {len(dataset)-5+i}", seq, height=60)
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
        
        sequence_input = st.text_input("Числовая последовательность:", placeholder="1 2 3 4")
        
        if st.button("Добавить последовательность и дообучить", type="primary"):
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
                    
                    # Создаем контейнер для прогресса
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
                    
                    # Очищаем анимацию и показываем реальный результат
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
        
        if st.button("Начать обучение", type="primary"):
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
                predictions = self.system.train(epochs=15)
                
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
        
        if st.button("Сгенерировать прогнозы", type="primary"):
            try:
                with st.spinner("AI анализирует паттерны..."):
                    predictions = self.system.predict()
                
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
                else:
                    st.warning("⚠️ Нет доступных прогнозов")
                    
            except Exception as e:
                st.error(f"Ошибка прогнозирования: {e}")

def main():
    st.title("🔢 AI Прогноз Числовых Последовательностей")
    st.write("Продвинутая нейросеть для анализа и прогнозирования числовых последовательностей")
    
    # Инициализация интерфейса
    interface = WebInterface()
    
    # Боковая панель с меню
    interface.show_status()
    
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