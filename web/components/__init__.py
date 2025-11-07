# [file name]: web/components/__init__.py
"""
Компоненты веб-сервиса для модульной архитектуры
"""

from .ml_adapter import MLSystemAdapter, create_ml_system
from .sidebar import show_sidebar
from .training_ui import show_training_ui
from .prediction_ui import show_prediction_ui
from .data_ui import show_data_ui
from .status_ui import show_status_ui
from .utils import (
    show_progress_messages,
    format_confidence_score,
    create_prediction_display,
    validate_and_format_group_input,
    get_system_status_badges,
    format_timestamp
)
from .styles import (
    apply_custom_styles,
    create_info_box,
    create_warning_box,
    create_success_box,
    highlight_text
)

__all__ = [
    'MLSystemAdapter',
    'create_ml_system',
    'show_sidebar', 
    'show_training_ui',
    'show_prediction_ui',
    'show_data_ui',
    'show_status_ui',
    'show_progress_messages',
    'format_confidence_score',
    'create_prediction_display',
    'validate_and_format_group_input',
    'get_system_status_badges',
    'format_timestamp',
    'apply_custom_styles',
    'create_info_box',
    'create_warning_box',
    'create_success_box',
    'highlight_text'
]