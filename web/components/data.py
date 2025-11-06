# web/components/data.py
import streamlit as st
from ml.data.data_loader import validate_group
from web.utils.session import get_system

def show_data_interface():
    """Интерфейс добавления данных - УЛУЧШЕННАЯ ВЕРСИЯ"""
    st.header("📥 Добавить данные")
    
    # Информация о текущем датасете
    system = get_system()
    status = system.get_status()
    st.info(f"Текущий размер датасета: {status['dataset_size']} групп")
    
    new_group = st.text_input(
        "Новая группа", 
        placeholder="Введите 4 числа через пробел (например: 1 2 3 4)",
        help="Формат: 4 числа от 1 до 26, без дублей в парах"
    )
    
    col1, col2 = st.columns([1, 3])
    
    with col1:
        if st.button("Добавить и дообучить", type="primary"):
            process_new_group(new_group)
    
    with col2:
        if st.button("Только добавить данные"):
            process_new_group(new_group, retrain=False)

def process_new_group(new_group, retrain=True):
    """Обработка новой группы данных"""
    if not new_group:
        st.warning("⚠️ Введите группу чисел")
        return
        
    if not validate_group(new_group):
        st.error("❌ Неверный формат группы. Используйте: 4 числа от 1 до 26, без дублей в парах")
        return
    
    system = get_system()
    
    try:
        if retrain:
            with st.spinner("Добавление данных и дообучение модели..."):
                predictions = system.add_data_and_retrain(new_group)
        else:
            with st.spinner("Добавление данных..."):
                # Только добавление данных без дообучения
                from ml.data.data_loader import load_dataset, save_dataset
                dataset = load_dataset()
                dataset.append(new_group)
                save_dataset(dataset)
                predictions = []
            
        if retrain and predictions:
            st.success("✅ Данные добавлены и модель дообучена!")
            
            st.subheader("Новые прогнозы:")
            for i, (group, score) in enumerate(predictions[:5], 1):
                st.write(f"{i}. `{group}` (вероятность: `{score:.3%}`)")
                
        elif not retrain:
            st.success("✅ Данные добавлены успешно!")
            
        # Обновляем статус
        new_status = system.get_status()
        st.info(f"📊 Новый размер датасета: {new_status['dataset_size']} групп")
        
    except Exception as e:
        st.error(f"❌ Ошибка при обработке данных: {e}")