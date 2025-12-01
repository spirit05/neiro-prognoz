#/opt/model/run_telegram_bot.sh
#!/bin/bash
# Скрипт запуска Telegram бота для новой ML системы

cd /opt/model

echo "🚀 Запуск Telegram бота для новой ML системы..."

# Создаем структуру директорий
echo "🔧 Проверка структуры директорий..."
python setup_directories.py

# Проверяем наличие виртуального окружения
if [ ! -d "venv" ]; then
    echo "❌ Виртуальное окружение не найдено"
    echo "Создайте его: python -m venv venv"
    exit 1
fi

# Активируем виртуальное окружение
source venv/bin/activate

# Проверяем наличие зависимостей
echo "📦 Проверка зависимостей..."
if ! pip list | grep -q "requests"; then
    echo "Установка зависимостей для Telegram бота..."
    pip install -r services/telegram/requirements-telegram.txt
fi

# Проверяем конфигурацию
CONFIG_FILE="config/telegram_config.yaml"
if [ ! -f "$CONFIG_FILE" ]; then
    echo "⚠️ Файл конфигурации не найден: $CONFIG_FILE"
    echo "Будет создан файл с настройками по умолчанию"
fi

# Запускаем бота
echo "🤖 Запуск Telegram бота..."
echo "📁 Логи будут сохраняться в: data/logs/telegram_bot.log"
echo "📋 Для остановки нажмите Ctrl+C"
echo "=" * 50

python -m services.telegram.bot

deactivate
echo "🛑 Telegram бот остановлен"
