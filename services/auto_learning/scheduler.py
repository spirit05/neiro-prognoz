#!/usr/bin/env python3
"""
Умный планировщик для автосервиса
"""

from datetime import datetime, timedelta

class SmartScheduler:
    def __init__(self):
        self.api_slots = [14, 29, 44, 59]  # Временные слоты API
    
    def calculate_next_run_time(self):
        """Расчет времени следующего запуска с учетом временных слотов"""
        now = datetime.now()
        current_minute = now.minute
        
        # Находим следующий слот
        next_slot = None
        for slot in self.api_slots:
            if current_minute < slot:
                next_slot = slot
                break
        
        # Если все слоты прошли в этом часе, берем первый слот следующего часа
        if next_slot is None:
            next_time = now.replace(hour=now.hour+1, minute=self.api_slots[0], second=0, microsecond=0)
        else:
            next_time = now.replace(minute=next_slot, second=0, microsecond=0)
        
        # Расчет интервала до следующего слота
        time_until_next = (next_time - now).total_seconds() / 60  # в минутах
        
        # Корректировка коротких интервалов
        if time_until_next < 4:
            time_until_next += 5  # добавляем 5 минут буфера
        
        return time_until_next
    
    def should_skip_due_to_buffer(self, minutes_to_draw: float) -> bool:
        """Проверка необходимости пропуска из-за временного буфера"""
        # Буфер 7 минут - пропуск если ≤7 минут до тиража
        if minutes_to_draw <= 7:
            return True
        return False
    
    def is_critical_interval(self, minutes_to_draw: float) -> bool:
        """Проверка критического интервала"""
        # Критический интервал ≤2 мин - экстренная остановка
        return minutes_to_draw <= 2