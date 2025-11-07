# [file name]: web/components/styles.py
"""
Стили и CSS для веб-интерфейса
"""

import streamlit as st

def apply_custom_styles():
    """Применение кастомных стилей к интерфейсу"""
    st.markdown("""
    <style>
    /* Основные стили */
    .main-header {
        font-size: 2.5rem;
        color: #1f77b4;
        text-align: center;
        margin-bottom: 2rem;
    }
    
    .sub-header {
        font-size: 1.8rem;
        color: #2e86ab;
        border-bottom: 2px solid #1f77b4;
        padding-bottom: 0.5rem;
        margin-top: 2rem;
    }
    
    /* Стили для карточек прогнозов */
    .prediction-card {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        border-radius: 10px;
        padding: 1.5rem;
        margin: 1rem 0;
        color: white;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
    }
    
    .prediction-number {
        font-size: 2rem;
        font-weight: bold;
        text-align: center;
    }
    
    .confidence-high {
        color: #00ff00;
        font-weight: bold;
    }
    
    .confidence-medium {
        color: #ffff00;
        font-weight: bold;
    }
    
    .confidence-low {
        color: #ff4444;
        font-weight: bold;
    }
    
    /* Стили для статусов */
    .status-success {
        background-color: #d4edda;
        border: 1px solid #c3e6cb;
        border-radius: 5px;
        padding: 0.75rem;
        margin: 0.5rem 0;
    }
    
    .status-warning {
        background-color: #fff3cd;
        border: 1px solid #ffeaa7;
        border-radius: 5px;
        padding: 0.75rem;
        margin: 0.5rem 0;
    }
    
    .status-error {
        background-color: #f8d7da;
        border: 1px solid #f5c6cb;
        border-radius: 5px;
        padding: 0.75rem;
        margin: 0.5rem 0;
    }
    
    /* Анимации */
    @keyframes fadeIn {
        from { opacity: 0; transform: translateY(20px); }
        to { opacity: 1; transform: translateY(0); }
    }
    
    .fade-in {
        animation: fadeIn 0.5s ease-in;
    }
    
    /* Стили для боковой панели */
    .sidebar-content {
        background: linear-gradient(180deg, #4facfe 0%, #00f2fe 100%);
        padding: 2rem 1rem;
        border-radius: 10px;
        margin: 1rem 0;
    }
    
    /* Адаптивность */
    @media (max-width: 768px) {
        .main-header {
            font-size: 2rem;
        }
        
        .prediction-card {
            padding: 1rem;
        }
        
        .prediction-number {
            font-size: 1.5rem;
        }
    }
    </style>
    """, unsafe_allow_html=True)

def create_info_box(title: str, content: str, icon: str = "ℹ️"):
    """Создать красивый информационный блок"""
    st.markdown(f"""
    <div class="fade-in" style="
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        border-radius: 10px;
        padding: 1.5rem;
        margin: 1rem 0;
        color: white;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
    ">
        <h3 style="margin: 0 0 1rem 0; color: white;">{icon} {title}</h3>
        <p style="margin: 0; color: white; opacity: 0.9;">{content}</p>
    </div>
    """, unsafe_allow_html=True)

def create_warning_box(title: str, content: str, icon: str = "⚠️"):
    """Создать предупреждающий блок"""
    st.markdown(f"""
    <div class="fade-in" style="
        background: linear-gradient(135deg, #ff9a9e 0%, #fecfef 100%);
        border-radius: 10px;
        padding: 1.5rem;
        margin: 1rem 0;
        color: #856404;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
    ">
        <h3 style="margin: 0 0 1rem 0; color: #856404;">{icon} {title}</h3>
        <p style="margin: 0; color: #856404; opacity: 0.9;">{content}</p>
    </div>
    """, unsafe_allow_html=True)

def create_success_box(title: str, content: str, icon: str = "✅"):
    """Создать блок успеха"""
    st.markdown(f"""
    <div class="fade-in" style="
        background: linear-gradient(135deg, #56ab2f 0%, #a8e6cf 100%);
        border-radius: 10px;
        padding: 1.5rem;
        margin: 1rem 0;
        color: #155724;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
    ">
        <h3 style="margin: 0 0 1rem 0; color: #155724;">{icon} {title}</h3>
        <p style="margin: 0; color: #155724; opacity: 0.9;">{content}</p>
    </div>
    """, unsafe_allow_html=True)

def highlight_text(text: str, color: str = "#1f77b4", size: str = "1.2rem"):
    """Выделить текст с цветом и размером"""
    return f'<span style="color: {color}; font-size: {size}; font-weight: bold;">{text}</span>'