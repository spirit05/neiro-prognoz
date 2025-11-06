# services/auto_learning/api_client.py
"""
API клиент для получения данных
"""
import subprocess
import json
import time
import requests
from datetime import datetime
from config.constants import MAX_API_RETRIES, API_RETRY_DELAY
from config.paths import INFO_JSON
from .file_manager import load_json_safe, save_json_safe

class APIClient:
    def __init__(self):
        self.max_retries = MAX_API_RETRIES
        self.retry_delay = API_RETRY_DELAY
    
    def prepare_uri(self):
        """Подготовка URI для запроса"""
        data = load_json_safe(INFO_JSON)
        current_draw_str = data.get('current_draw', '0')

        try:
            current_draw = int(current_draw_str)
            next_draw = current_draw + 1
        except (ValueError, TypeError):
            next_draw = 1

        url = f"https://www.stoloto.ru/p/api/mobile/api/v35/service/games/details/draw-combination?game=dvazhdydva&draw={next_draw}"
        
        return str(next_draw), url
    
    def call_api(self):
        """Вызов API с повторными попытками"""
        draw, url = self.prepare_uri()
        
        for attempt in range(self.max_retries):
            try:
                result = subprocess.run([
                    'curl', 
                    '-s', '--max-time', '30',
                    '-H', 'User-Agent: Mozilla/5.0', 
                    '-H', 'Accept: application/json, text/plain, */*',
                    '-H', 'Device-Platform: WEB_MOBILE_LINUX',
                    '-H', 'Device-Type: MOBILE', 
                    '-H', 'Gosloto-Partner: bXMjXFRXZ3coWXh6R3s1NTdUX3dnWlBMLUxmdg',
                    '-H', 'gosloto-token: 76b9725602-dcfb02-4fb151-b0df27-949295930e0c26', 
                    '-H', 'referer: https://www.stoloto.ru/dvazhdydva/archive',
                    url
                ], capture_output=True, text=True, check=True, timeout=35)
                
                if result.returncode == 0:
                    response_data = json.loads(result.stdout)
                    
                    if 'combination' not in response_data or 'structured' not in response_data['combination']:
                        continue
                    
                    combination_structured = response_data['combination']['structured']
                    combination_string = " ".join(str(num) for num in combination_structured)
                    
                    self._save_api_result(draw, combination_string)
                    return response_data
                    
            except Exception as e:
                if attempt < self.max_retries - 1:
                    time.sleep(self.retry_delay)
                else:
                    raise e
        
        return None
    
    def _save_api_result(self, draw, combination):
        """Сохранение результата API"""
        data = load_json_safe(INFO_JSON)
        
        if 'history' not in data:
            data['history'] = []
        
        # Проверяем дубликаты
        for entry in data['history']:
            if entry.get('draw') == draw:
                return
        
        # Проверяем последовательность
        if data.get('history'):
            last_draw = int(data['history'][-1]['draw'])
            current_draw = int(draw)
            if current_draw != last_draw + 1:
                return
        
        # Добавляем новую запись
        new_entry = {
            'draw': draw,
            'combination': combination,
            'timestamp': datetime.now().isoformat(),
            'processed': False,
            'service_type': 'api_request'
        }
        
        data['history'].append(new_entry)
        data['current_draw'] = draw
        
        save_json_safe(data, INFO_JSON)