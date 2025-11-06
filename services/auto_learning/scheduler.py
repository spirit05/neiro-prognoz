# services/auto_learning/scheduler.py
"""
Умное расписание для автосервиса
"""
import schedule
import time
from datetime import datetime, timedelta
from config.constants import SCHEDULE_MINUTES, BUFFER_MINUTES, CRITICAL_INTERVAL_MINUTES

class SmartScheduler:
    def __init__(self):
        self.schedule_minutes = SCHEDULE_MINUTES
        self.buffer_minutes = BUFFER_MINUTES
        self.critical_interval = CRITICAL_INTERVAL_MINUTES
        self.next_scheduled_run = None
    
    def calculate_next_run_time(self, current_time=None):
        """Расчет следующего времени запуска с учетом буфера"""
        if current_time is None:
            current_time = datetime.now()
        
        current_minute = current_time.minute
        
        # Находим следующий временной слот
        next_minute = None
        for minute in self.schedule_minutes:
            if current_minute < minute:
                next_minute = minute
                break
        
        # Если все слоты прошли в этом часе, берем первый слот следующего часа
        if next_minute is None:
            next_time = current_time.replace(
                hour=current_time.hour + 1, 
                minute=self.schedule_minutes[0], 
                second=0, 
                microsecond=0
            )
            time_until_next = (next_time - current_time).total_seconds() / 60
        else:
            next_time = current_time.replace(minute=next_minute, second=0, microsecond=0)
            time_until_next = (next_time - current_time).total_seconds() / 60
        
        # Применяем логику буфера и критических интервалов
        if time_until_next <= self.critical_interval:
            # Критический интервал - слишком близко к временному слоту
            return 0, "critical"
        elif time_until_next <= self.buffer_minutes:
            # Используем буфер
            return self.buffer_minutes, "buffer"
        else:
            # Нормальный интервал
            self.next_scheduled_run = next_time
            return time_until_next, "normal"
    
    def setup_adaptive_schedule(self, task_function):
        """Настройка адаптивного расписания"""
        schedule.clear()
        
        # Расчет первого интервала
        next_interval, interval_type = self.calculate_next_run_time()
        
        if next_interval == 0 and interval_type == "critical":
            return False, "critical_interval"
        
        if next_interval > 0:
            # Планируем следующий запуск через расчетный интервал
            schedule.every(next_interval).minutes.do(task_function)
            
            # После корректировки переходим на стандартное расписание
            for minute in self.schedule_minutes:
                schedule.every().hour.at(f":{minute:02d}").do(task_function)
            
            return True, f"adaptive_{interval_type}"
        
        return False, "unknown_error"
    
    def run_pending(self):
        """Выполнение запланированных задач"""
        return schedule.run_pending()
    
    def clear_schedule(self):
        """Очистка расписания"""
        schedule.clear()