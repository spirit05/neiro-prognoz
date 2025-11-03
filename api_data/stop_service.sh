# api_data/stop_service.sh
#!/bin/bash
# Скрипт остановки сервиса автообучения

cd /opt/project/api_data

if [ ! -f "service.pid" ]; then
    echo "❌ Файл service.pid не найден. Сервис может быть не запущен."
    exit 1
fi

PID=$(cat service.pid)

if ps -p $PID > /dev/null; then
    echo "🛑 Останавливаем сервис с PID: $PID"
    kill $PID
    rm service.pid
    echo "✅ Сервис остановлен"
else:
    echo "⚠️ Процесс с PID $PID не найден. Удаляю service.pid"
    rm service.pid
fi