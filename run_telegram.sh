#!/bin/bash

# Скрипт запуска Telegram бота
# Использование: ./run_telegram.sh

echo "📱 Запуск Telegram бота..."

# Активируем venv
source ./venv.sh

# Запускаем Telegram бота
echo "🚀 Запуск Telegram бота..."
cd /opt/dev
python3 services/telegram/bot.py

