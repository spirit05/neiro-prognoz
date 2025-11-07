# /opt/dev/utils/system_monitor.py
import psutil
import subprocess
from datetime import datetime

class SystemMonitor:
    @staticmethod
    def get_full_status():
        """Полный статус всей системы"""
        status = {
            'timestamp': datetime.now().isoformat(),
            'services': {},
            'resources': {},
            'ml_system': {}
        }
        
        # Проверка сервисов
        services = [
            'sequence-predictor-web.service',
            'telegram-bot.service'
        ]
        
        for service in services:
            try:
                result = subprocess.run(
                    ['systemctl', 'is-active', service],
                    capture_output=True, text=True
                )
                status['services'][service] = result.stdout.strip()
            except Exception as e:
                status['services'][service] = f'error: {e}'
        
        # Проверка ресурсов
        status['resources'] = {
            'cpu_percent': psutil.cpu_percent(),
            'memory_percent': psutil.virtual_memory().percent,
            'disk_usage': psutil.disk_usage('/').percent
        }
        
        return status