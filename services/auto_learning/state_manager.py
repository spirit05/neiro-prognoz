#!/usr/bin/env python3
"""
Менеджер состояния сервиса
"""

import os
import json
from datetime import datetime
from typing import Dict, Any

class StateManager:
    def __init__(self):
        self.project_root = '/opt/dev'
        self.state_path = os.path.join(self.project_root, 'data', 'service_state.json')
    
    def load_state(self) -> Dict[str, Any]:
        """Загрузка состояния сервиса"""
        try:
            if os.path.exists(self.state_path):
                with open(self.state_path, 'r', encoding='utf-8') as f:
                    return json.load(f)
            return {}
        except Exception as e:
            print(f"⚠️ Не удалось загрузить состояние сервиса: {e}")
            return {}
    
    def save_state(self, state: Dict[str, Any]) -> bool:
        """Сохранение состояния сервиса"""
        try:
            os.makedirs(os.path.dirname(self.state_path), exist_ok=True)
            
            state['last_update'] = datetime.now().isoformat()
            
            with open(self.state_path, 'w', encoding='utf-8') as f:
                json.dump(state, f, ensure_ascii=False, indent=2)
            
            return True
        except Exception as e:
            print(f"❌ Ошибка сохранения состояния сервиса: {e}")
            return False
    
    def get_service_status(self) -> Dict[str, Any]:
        """Получение текущего статуса сервиса"""
        state = self.load_state()
        return {
            'service_active': state.get('service_active', True),
            'last_processed_draw': state.get('last_processed_draw'),
            'consecutive_api_errors': state.get('consecutive_api_errors', 0),
            'last_update': state.get('last_update'),
            'service_type': 'auto_learning'
        }