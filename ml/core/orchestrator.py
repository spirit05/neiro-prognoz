# [file name]: ml/core/orchestrator.py
"""
ФАСАД ДЛЯ ОБРАТНОЙ СОВМЕСТИМОСТИ
Этот файл оставлен для обеспечения обратной совместимости со старыми импортами.
Вся новая функциональность находится в модульной структуре ml/core/orchestrator/
"""

import warnings
warnings.warn(
    "Прямой импорт из ml.core.orchestrator устарел. "
    "Используйте from ml.core.orchestrator import MLOrchestrator",
    DeprecationWarning,
    stacklevel=2
)

# Перенаправляем на новую модульную реализацию
from .orchestrator import MLOrchestrator

__all__ = ['MLOrchestrator']
