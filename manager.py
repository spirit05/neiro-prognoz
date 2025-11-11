# Перезагружаем systemd
sudo systemctl daemon-reload

# Включаем автозапуск
sudo systemctl enable ai-web.service
sudo systemctl enable ai-bot.service

# Запускаем сервисы
sudo systemctl start ai-web.service
sudo systemctl start ai-bot.service
ml-auto

# Проверяем статус
sudo systemctl status ai-web.service
sudo systemctl status ai-bot.service

# Смотрим логи
sudo journalctl -u ai-web.service -f
sudo journalctl -u ai-bot.service -f

# Остановить сервис
sudo systemctl stop ai-web.service

# Перезапустить сервис
sudo systemctl restart ai-web.service

# Просмотр логов
sudo journalctl -u ai-web.service -n 50
sudo journalctl -u ai-bot.service --since "1 hour ago"

# Проверить все сервисы
sudo systemctl list-units | grep ai

Вот команды для просмотра systemd процессов:

## 1. Просмотр всех сервисов
```bash
# Все загруженные сервисы
sudo systemctl list-units --type=service

# Все сервисы (включая неактивные)
sudo systemctl list-units --type=service --all

# Только запущенные сервисы
sudo systemctl list-units --type=service --state=running

# Только failed сервисы
sudo systemctl list-units --type=service --state=failed
```

## 2. Фильтрация по имени
```bash
# Найти сервисы по имени
sudo systemctl list-units --type=service | grep ai

# Или так
sudo systemctl list-units '*ai*'
```

## 3. Детальная информация о конкретном сервисе
```bash
# Статус конкретного сервиса
sudo systemctl status ai-web.service
sudo systemctl status ai-bot.service

# Показать все свойства сервиса
sudo systemctl show ai-web.service
```

## 4. Просмотр логов
```bash
# Логи в реальном времени
sudo journalctl -u ai-web.service -f

# Логи за последний час
sudo journalctl -u ai-web.service --since "1 hour ago"

# Логи за сегодня
sudo journalctl -u ai-web.service --since today

# Последние 100 строк логов
sudo journalctl -u ai-web.service -n 100

# Логи с временными метками
sudo journalctl -u ai-web.service -o short-precise
```

## 5. Другие полезные команды
```bash
# Просмотр всех юнитов systemd
sudo systemctl list-units

# Просмотр всех таймеров
sudo systemctl list-timers

# Просмотр зависимостей сервиса
sudo systemctl list-dependencies ai-web.service

# Проверить, включен ли автозапуск
sudo systemctl is-enabled ai-web.service
```

## 6. Для твоих сервисов ai:
```bash
# Проверить все ai сервисы
sudo systemctl list-units | grep ai

# Или более детально
sudo systemctl status ai-*.service

# Посмотреть логи всех ai сервисов
sudo journalctl -u ai-*.service --since "10 minutes ago"
```

## 7. Если нужно найти конкретный процесс:
```bash
# Найти процессы по имени
ps aux | grep streamlit
ps aux | grep python

# Найти PID сервиса
sudo systemctl show ai-web.service --property=MainPID
```

Теперь ты можешь легко мониторить все systemd процессы! 🎯
