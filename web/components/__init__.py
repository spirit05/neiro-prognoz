# [file name]: web/components/__init__.py
"""
Компоненты веб-интерфейса
"""

from .navigation_sidebar import NavigationSidebar
from .data_dashboard import DataDashboard
from .training_control import TrainingControl
from .prediction_interface import PredictionInterface
from .group_addition import GroupAddition
from .system_monitor import SystemMonitor
from .styles import apply_custom_styles

__all__ = [
    'NavigationSidebar',
    'DataDashboard', 
    'TrainingControl',
    'PredictionInterface',
    'GroupAddition',
    'SystemMonitor',
    'apply_custom_styles'
]
