# [file name]: web/components/utils.py
"""
Вспомогательные функции для веб-интерфейса
"""

import streamlit as st
from datetime import datetime
from typing import List

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