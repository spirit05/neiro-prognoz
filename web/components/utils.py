# [file name]: web/components/utils.py
"""
Вспомогательные функции для веб-интерфейса
"""

import streamlit as st
from datetime import datetime
from typing import List, Dict, Optional, Tuple
import time

def show_progress_messages(messages: List[str], height: int = 200):
    """Показать сообщения прогресса"""
    if messages:
        recent_messages = messages[-10:]  # Последние 10 сообщений
        st.text_area(
            "📝 Ход выполнения:", 
            "\n".join(recent_messages), 
            height=height,
            key="progress_display"
        )

def show_operation_progress(operation_type: str, current_step: int, total_steps: int, current_message: str = ""):
    """Показать прогресс операции с этапами"""
    
    steps_info = {
        "training": [
            "📊 Загрузка данных...",
            "🧠 Обучение нейросети...", 
            "🏗️ Создание ансамблевой системы...",
            "🔮 Генерация прогнозов...",
            "💾 Сохранение модели..."
        ],
        "add_data": [
            "📝 Валидация данных...",
            "🔍 Сравнение с прогнозами...",
            "🔄 Дообучение модели...",
            "🔮 Генерация новых прогнозов...",
            "💾 Сохранение результатов..."
        ],
        "prediction": [
            "📊 Анализ истории...",
            "🧠 Применение модели...",
            "🏗️ Ансамблевое предсказание...", 
            "📈 Расчет уверенности...",
            "💾 Сохранение прогнозов..."
        ]
    }
    
    steps = steps_info.get(operation_type, [f"Шаг {i+1}" for i in range(total_steps)])
    
    # Прогресс-бар
    progress = current_step / total_steps
    st.progress(progress)
    
    # Текущий этап
    if current_step < total_steps:
        st.info(f"**{steps[current_step]}** {current_message}")
    
    # Предыдущие завершенные этапы
    for i in range(current_step):
        st.success(f"✅ {steps[i]}")
    
    # Предстоящие этапы
    for i in range(current_step + 1, total_steps):
        st.text(f"⏳ {steps[i]}")

def show_recent_logs(messages: List[str], max_logs: int = 3):
    """Показать последние логи в компактном формате"""
    if messages:
        recent_logs = messages[-max_logs:]
        
        st.markdown("""
        <div style='
            background: #f8f9fa; 
            border: 1px solid #e9ecef; 
            border-radius: 8px; 
            padding: 1rem; 
            margin: 1rem 0;
            font-family: monospace;
            font-size: 0.9rem;
        '>
        """, unsafe_allow_html=True)
        
        st.markdown("**📊 Последние действия:**")
        
        for log in recent_logs:
            clean_log = log.split(' - ')[-1] if ' - ' in log else log
            st.markdown(f"• {clean_log}")
        
        st.markdown("</div>", unsafe_allow_html=True)

def format_confidence_score(score: float) -> tuple:
    """Форматирование оценки уверенности"""
    if score > 0.01:
        return "🟢 ВЫСОКАЯ", "success"
    elif score > 0.001:
        return "🟡 СРЕДНЯЯ", "warning"
    else:
        return "🔴 НИЗКАЯ", "error"

def create_prediction_display(predictions: List[tuple], columns: int = 2):
    """Создать отображение прогнозов в колонках"""
    if not predictions:
        st.info("📝 Прогнозы не сгенерированы")
        return
    
    cols = st.columns(columns)
    
    for i, (group, score) in enumerate(predictions):
        confidence_text, _ = format_confidence_score(score)
        
        with cols[i % columns]:
            st.metric(
                label=f"Прогноз #{i+1}",
                value=f"{group[0]} {group[1]} {group[2]} {group[3]}",
                delta=f"{score:.4f}"
            )
            st.caption(f"Уверенность: {confidence_text}")

def validate_and_format_group_input(group_str: str) -> tuple:
    """Валидация и форматирование ввода группы"""
    from ml.utils.data_utils import validate_group
    
    if not group_str.strip():
        return False, "❌ Введите последовательность"
    
    if not validate_group(group_str):
        return False, "❌ Неверный формат! Должно быть 4 числа 1-26 через пробел"
    
    return True, "✅ Формат корректен"

def validate_and_format_groups_input(groups_str: str) -> List[Dict[str, str]]:
    """Валидация и форматирование ввода группы"""
    from ml.utils.data_utils import validate_group

    if not groups_str.strip():
        return []
        
    str_list = groups_str.split('\n')
    group = []

    for s in str_list:
        # Разделяем по табуляции и пробелам, затем фильтруем пустые строки
        parts = [part for part in s.replace('\t', ' ').split(' ') if part]
            
        temp_group = {
            'draw': parts[0],
            'combination': parts[-1].replace(',', ' ')
        }
        
        if not validate_group(temp_group.get('combination')): 
            group = []
            break
        else:
            group.append(temp_group)

    reverse_group = group[::-1]
    
    return reverse_group

def get_system_status_badges(status: dict) -> List[str]:
    """Получить бейджи статуса системы"""
    badges = []
    
    if status.get('is_trained', False):
        badges.append("✅ Обучена")
    else:
        badges.append("⚠️ Не обучена")
    
    if status.get('has_sufficient_data', False):
        badges.append("📊 Данные OK")
    else:
        badges.append("📉 Мало данных")
    
    if status.get('architecture') == 'НОВАЯ МОДУЛЬНАЯ':
        badges.append("🏗️ Модульная")
    
    return badges

def format_timestamp(timestamp: str = None) -> str:
    """Форматирование временной метки"""
    if timestamp:
        try:
            dt = datetime.fromisoformat(timestamp.replace('Z', '+00:00'))
            return dt.strftime('%H:%M:%S %d.%m.%Y')
        except:
            return timestamp
    return datetime.now().strftime('%H:%M:%S %d.%m.%Y')
