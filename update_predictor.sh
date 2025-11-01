#!/bin/bash
# update_predictor.sh

echo "🔄 Обновление Sequence Predictor системы..."

# Останавливаем сервис
sudo systemctl stop sequence-predictor.service

# Делаем backup текущей версии
BACKUP_DIR="/backup/sequence-predictor-$(date +%Y%m%d-%H%M%S)"
mkdir -p $BACKUP_DIR
cp -r /path/to/your/project/* $BACKUP_DIR/ 2>/dev/null || true

# Копируем новые файлы (предполагая, что они в текущей директории)
cp *.py /path/to/your/project/
cp -r model /path/to/your/project/

# Устанавливаем права
chmod +x /path/to/your/project/run.py
chown -R root:root /path/to/your/project

# Перезагружаем systemd
sudo systemctl daemon-reload

# Запускаем сервис
sudo systemctl start sequence-predictor.service

# Проверяем статус
echo "⏳ Ожидание запуска..."
sleep 3
sudo systemctl status sequence-predictor.service

echo "✅ Обновление завершено!"