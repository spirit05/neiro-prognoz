#!/bin/bash

# Скрипт запуска автосервиса
# Использование: ./run_auto.sh [команда]

COMMAND=${1:-"--status"}  # По умолчанию показываем статус

echo "🤖 Запуск автосервиса..."
cd /opt/dev
# Активируем venv
source ./venv.sh

# Запускаем автосервис
echo "Убиваем старые процессы"
pkill -f "python.*service.*auto_learning"
echo "презапускаем автосервис"
nohup python3 services/auto_learning/service.py --restart 
echo "🚀 Запуск автосервиса"
echo "Запускаем с исправленной синхронизацией"
nohup python3 services/auto_learning/service.py --schedule > /opt/dev/data/logs/auto_learning_sync_fixed.log 2>&1 &
echo " Смотрим логи - ДОЛЖНА БЫТЬ СИНХРОНИЗАЦИЯ"
tail -f /opt/dev/data/logs/auto_learning_sync_fixed.log
