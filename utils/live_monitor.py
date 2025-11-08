# /opt/dev/utils/live_monitor.py
#!/usr/bin/env python3
"""
Мониторинг логов в реальном времени - аналог tail -f для всех сервисов
"""

import os
import time
import threading
import subprocess
from datetime import datetime
from pathlib import Path
import psutil

class LiveLogMonitor:
    def __init__(self):
        self.project_root = Path('/opt/dev')
        
        # Основные логи
        self.log_files = {
            'auto_learning': self.project_root / 'data' / 'logs' / 'auto_learning.log',
            'telegram_bot': self.project_root / 'data' / 'logs' / 'telegram_bot.log', 
            'ml_system': self.project_root / 'data' / 'logs' / 'ml_system.log',
        }
        
        # Находим логи Streamlit
        self._find_streamlit_logs()
        
        # Позиции чтения для каждого файла
        self.file_positions = {}
        self.running = True
        
        # Статистика
        self.stats = {
            'start_time': datetime.now(),
            'lines_processed': 0,
            'errors_detected': 0,
            'warnings_detected': 0
        }
        
        # Флаг первого отображения
        self.first_display = True
    
    def _find_streamlit_logs(self):
        """Поиск логов Streamlit"""
        possible_paths = [
            Path.home() / '.streamlit' / 'logs',
            Path.home() / '.streamlit' / 'log.txt',
            Path('/var/log/streamlit'),
            self.project_root / 'streamlit.log',
            self.project_root / 'logs' / 'streamlit.log',
            self.project_root / 'web' / 'streamlit.log',
            Path('/tmp/streamlit.log'),
        ]
        
        # Также проверяем вывод процессов Streamlit
        try:
            result = subprocess.run(['pgrep', '-f', 'streamlit'], capture_output=True, text=True)
            if result.returncode == 0:
                pids = result.stdout.strip().split('\n')
                for pid in pids:
                    if pid:
                        self.log_files[f'streamlit_pid_{pid}'] = f'/proc/{pid}/fd/1'  # stdout
                        self.log_files[f'streamlit_pid_{pid}_err'] = f'/proc/{pid}/fd/2'  # stderr
        except:
            pass
        
        # Добавляем найденные файлы
        for path in possible_paths:
            if path.exists():
                if path.is_dir():
                    log_files = list(path.glob('*.log'))
                    for log_file in log_files:
                        self.log_files[f'streamlit_{log_file.name}'] = log_file
                else:
                    self.log_files[f'streamlit_{path.name}'] = path
        
        # Если не нашли логи Streamlit, создаем свой лог для веб-сервиса
        if not any('streamlit' in key for key in self.log_files.keys()):
            web_log_path = self.project_root / 'data' / 'logs' / 'web_service.log'
            web_log_path.parent.mkdir(exist_ok=True)
            self.log_files['web_service'] = web_log_path
    
    def tail_file(self, filename, callback):
        """Аналог tail -f для одного файла"""
        file_path = Path(filename) if isinstance(filename, str) else filename
        
        # Пропускаем специальные файлы которые могут не существовать
        if isinstance(filename, str) and filename.startswith('/proc/'):
            if not file_path.exists():
                return
        
        # Если файла нет - ждем его создания
        while not file_path.exists() and self.running:
            time.sleep(1)
        
        if not self.running:
            return
            
        try:
            # Запоминаем позицию (конец файла)
            self.file_positions[filename] = file_path.stat().st_size
        except:
            # Если не можем получить размер, начинаем с начала
            self.file_positions[filename] = 0
        
        while self.running:
            try:
                with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                    # Переходим на сохраненную позицию
                    f.seek(self.file_positions[filename])
                    
                    # Читаем новые строки
                    new_lines = []
                    for line in f:
                        new_lines.append(line.strip())
                    
                    # Если есть новые строки - обрабатываем
                    if new_lines:
                        for line in new_lines:
                            if line:  # Игнорируем пустые строки
                                callback(filename, line)
                        
                        # Обновляем статистику
                        self.stats['lines_processed'] += len(new_lines)
                    
                    # Обновляем позицию
                    self.file_positions[filename] = f.tell()
                    
            except Exception as e:
                # Для /proc файлов ошибки нормальны
                if not str(filename).startswith('/proc/'):
                    print(f"❌ Ошибка чтения {filename}: {e}")
            
            # Ждем перед следующей проверкой
            time.sleep(0.5)
    
    def process_log_line(self, filename, line):
        """Обработка одной строки лога"""
        # Определяем сервис по имени файла
        service_name = "unknown"
        for key, path in self.log_files.items():
            if str(filename) == str(path):
                service_name = key
                break
        
        # Определяем тип сообщения по ключевым словам
        color = '🟢'  # INFO по умолчанию
        
        if any(keyword in line for keyword in ['ERROR', '❌', '🚨', 'error', 'Error']):
            color = '🔴'
            self.stats['errors_detected'] += 1
        elif any(keyword in line for keyword in ['WARNING', '⚠️', '🔍', 'warning', 'Warning']):
            color = '🟡'
            self.stats['warnings_detected'] += 1
        elif any(keyword in line for keyword in ['DEBUG', '🔍', 'debug', 'Debug']):
            color = '🔵'
        
        # Форматируем вывод
        if ' - ' in line:
            parts = line.split(' - ', 3)
            if len(parts) >= 4:
                timestamp, logger, level, message = parts
                # Берем только время (без даты)
                time_only = timestamp.split(' ')[1] if ' ' in timestamp else timestamp
                display_line = f"{color} {time_only} | {service_name:20} | {message}"
            else:
                display_line = f"{color} {service_name:20} | {line}"
        else:
            # Для Streamlit логов без формата
            display_line = f"{color} {service_name:20} | {line}"
        
        # Выводим в консоль
        print(display_line)
    
    def get_system_status(self):
        """Получение текущего статуса системы"""
        try:
            status = {
                'timestamp': datetime.now().strftime('%H:%M:%S'),
                'cpu': f"{psutil.cpu_percent()}%",
                'memory': f"{psutil.virtual_memory().percent}%",
                'processes': {}
            }
            
            # Проверяем процессы проекта
            for proc in psutil.process_iter(['pid', 'name', 'cmdline']):
                try:
                    cmdline = proc.info['cmdline']
                    if cmdline and 'python' in cmdline[0]:
                        # Определяем тип сервиса
                        service_name = 'unknown'
                        cmd_str = ' '.join(cmdline)
                        
                        if 'streamlit' in cmd_str:
                            if '8501' in cmd_str:
                                service_name = 'web_prod'
                            elif '8502' in cmd_str:
                                service_name = 'web_dev'
                            else:
                                service_name = 'web_streamlit'
                        elif 'telegram' in cmd_str:
                            service_name = 'telegram_bot'
                        elif 'auto_learning' in cmd_str:
                            service_name = 'auto_learning'
                        elif 'ml' in cmd_str:
                            service_name = 'ml_system'
                        
                        if service_name != 'unknown':
                            status['processes'][service_name] = {
                                'pid': proc.info['pid'],
                                'memory_mb': proc.memory_info().rss // 1024 // 1024,
                                'port': '8501' if '8501' in cmd_str else '8502' if '8502' in cmd_str else 'N/A'
                            }
                except (psutil.NoSuchProcess, psutil.AccessDenied):
                    continue
            
            return status
        except Exception as e:
            return {'error': str(e)}
    
    def display_status_header(self):
        """Отображение заголовка с текущим статусом - ТОЛЬКО ПРИ СТАРТЕ"""
        if not self.first_display:
            return
            
        status = self.get_system_status()
        
        print("\n" + "="*80)
        print(f"🎯 LIVE MONITOR | Время: {status['timestamp']} | CPU: {status['cpu']} | Память: {status['memory']}")
        print("="*80)
        
        # Процессы
        if status['processes']:
            print("🟢 Запущенные сервисы:")
            for service, info in status['processes'].items():
                port_info = f" (порт {info['port']})" if info['port'] != 'N/A' else ""
                print(f"   📍 {service}: PID {info['pid']} ({info['memory_mb']}MB){port_info}")
        else:
            print("🔴 Нет запущенных сервисов")
        
        # Логи которые мониторятся
        print(f"\n📊 Мониторинг логов ({len(self.log_files)} файлов):")
        for log_name in sorted(self.log_files.keys()):
            log_path = self.log_files[log_name]
            exists = "✅" if Path(log_path).exists() else "❌"
            print(f"   {exists} {log_name}")
        
        print("-"*80)
        print("📊 Журнал логов в реальном времени:")
        print("-"*80)
        
        self.first_display = False
    
    def start_monitoring(self):
        """Запуск мониторинга в реальном времени"""
        print("🚀 Запуск мониторинга логов в реальном времени...")
        print("💡 Нажмите Ctrl+C для остановки")
        
        # Показываем заголовок только один раз
        self.display_status_header()
        
        # Потоки для каждого файла логов
        threads = []
        
        for log_name, log_path in self.log_files.items():
            if Path(log_path).exists():
                thread = threading.Thread(
                    target=self.tail_file, 
                    args=(log_path, self.process_log_line),
                    daemon=True
                )
                threads.append(thread)
                thread.start()
            else:
                print(f"⚠️  Файл не найден: {log_path}")
        
        try:
            # Главный цикл - просто ждем, заголовок больше не обновляем
            while self.running:
                time.sleep(1)
                
        except KeyboardInterrupt:
            print("\n🛑 Остановка мониторинга...")
            self.running = False
        
        # Ждем завершения потоков
        for thread in threads:
            thread.join(timeout=1)
        
        # Финальная статистика
        duration = datetime.now() - self.stats['start_time']
        print(f"\n📊 СТАТИСТИКА МОНИТОРИНГА:")
        print(f"   ⏱️  Длительность: {duration}")
        print(f"   📄 Обработано строк: {self.stats['lines_processed']}")
        print(f"   ⚠️  Предупреждений: {self.stats['warnings_detected']}")
        print(f"   ❌ Ошибок: {self.stats['errors_detected']}")

class AdvancedLiveMonitor(LiveLogMonitor):
    """Расширенный мониторинг с фильтрацией и поиском"""
    
    def __init__(self):
        super().__init__()
        self.filters = {
            'show_errors': True,
            'show_warnings': True, 
            'show_info': True,
            'show_debug': False,
            'search_term': None
        }
    
    def set_filter(self, **kwargs):
        """Установка фильтров отображения"""
        self.filters.update(kwargs)
    
    def process_log_line(self, filename, line):
        """Обработка с фильтрацией"""
        # Применяем фильтры
        should_display = True
        
        if not self.filters['show_errors'] and any(keyword in line for keyword in ['ERROR', '❌', '🚨']):
            should_display = False
        elif not self.filters['show_warnings'] and any(keyword in line for keyword in ['WARNING', '⚠️']):
            should_display = False
        elif not self.filters['show_info'] and not any(keyword in line for keyword in ['ERROR', 'WARNING', '❌', '⚠️', '🚨']):
            should_display = False
        
        # Поиск по термину
        if self.filters['search_term'] and self.filters['search_term'].lower() not in line.lower():
            should_display = False
        
        if should_display:
            super().process_log_line(filename, line)

def main():
    """Основная функция запуска"""
    import argparse
    
    parser = argparse.ArgumentParser(description='Live Log Monitor')
    parser.add_argument('--service', help='Мониторинг только одного сервиса')
    parser.add_argument('--no-errors', action='store_true', help='Скрыть ошибки')
    parser.add_argument('--no-warnings', action='store_true', help='Скрыть предупреждения')
    parser.add_argument('--only-errors', action='store_true', help='Только ошибки')
    parser.add_argument('--search', help='Поиск по тексту в логах')
    parser.add_argument('--status', action='store_true', help='Показать текущий статус')
    
    args = parser.parse_args()
    
    monitor = AdvancedLiveMonitor()
    
    # Применяем фильтры
    if args.service:
        # Оставляем только указанный сервис
        filtered_files = {}
        for key, path in monitor.log_files.items():
            if args.service in key:
                filtered_files[key] = path
        monitor.log_files = filtered_files
    
    if args.no_errors:
        monitor.set_filter(show_errors=False)
    if args.no_warnings:
        monitor.set_filter(show_warnings=False)
    if args.only_errors:
        monitor.set_filter(show_errors=True, show_warnings=False, show_info=False)
    if args.search:
        monitor.set_filter(search_term=args.search)
    
    # Если нужно показать только статус
    if args.status:
        monitor.display_status_header()
        return
    
    # Запускаем мониторинг
    monitor.start_monitoring()

if __name__ == "__main__":
    main()
