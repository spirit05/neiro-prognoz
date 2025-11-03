# api_data/start_service.sh
#!/bin/bash
# Скрипт запуска сервиса автообучения

cd /opt/project/api_data

# Проверяем наличие Python
if ! command -v python3 &> /dev/null; then
    echo "❌ Python3 не найден"
    exit 1
fi

# Проверяем наличие необходимых файлов
if [ ! -f "auto_learning_service.py" ]; then
    echo "❌ Файл auto_learning_service.py не найден"
    exit 1
fi

echo "🎯 Запуск сервиса автообучения..."
echo "📝 Логи будут сохраняться в service_runner.log"

# Запускаем сервис в фоне
nohup python3 service_runner.py >> service_runner.log 2>&1 &

# Сохраняем PID
echo $! > service.pid

echo "✅ Сервис запущен с PID: $(cat service.pid)"
echo "🔍 Для проверки статуса: python3 check_service.py"
echo "🛑 Для остановки: ./stop_service.sh"