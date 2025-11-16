# /opt/model/__init__.py
"""
Пакет новой ML системы
"""

import sys
import os

# Добавляем текущую директорию в Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

__version__ = "1.0.0"
__author__ = "ML System Team"
