#/opt/model/services/telegram/README.md
# Telegram Bot для новой ML системы

## 📋 Обзор

Telegram бот для управления AI Prediction System на основе новой модульной архитектуры. Бот использует только **WorkflowManager** для всех операций, аналогично веб-интерфейсу.

## 🏗 Архитектура
Telegram Bot (services/telegram/)
├── bot.py # Основной класс бота
├── ml_dispatcher.py # Интеграция с WorkflowManager (аналог MLIntegration)
├── config.py # Конфигурация бота (YAML)
├── security.py # Безопасность и проверка доступа
├── commands.py # Все команды бота
├── handlers.py # Обработчики сообщений
└── init.py


## 🔧 Установка и настройка

### 1. Настройка конфигурации

Создайте файл `/opt/model/config/telegram_config.yaml`:

```yaml
telegram:
  bot_token: "ВАШ_BOT_TOKEN"  # Получить у @BotFather
  chat_id: "ВАШ_CHAT_ID"      # ID чата для уведомлений
  
  notifications:
    training_complete: true
    predictions_generated: true
    errors: true
    warnings: true
  
  polling:
    timeout: 30
    interval: 1
  
  security:
    allowed_users: []
    require_auth: true
```

cd /opt/model
pip install -r services/telegram/requirements-telegram.txt

# Способ 1: Прямой запуск
python -m services.telegram.bot

# Способ 2: Через скрипт
chmod +x run_telegram_bot.sh
./run_telegram_bot.sh

# Способ 3: В фоновом режиме
nohup python -m services.telegram.bot > telegram_bot.log 2>&1 &

📋 Доступные команды
Информационные команды
/start - Начало работы

/help - Справка по командам

/status - Полный статус системы

/version - Версия системы

/system - Детальная информация

Команды данных
/data - Информация о датасете

/add [1 2 3 4] - Добавить группу вручную

Команды управления ML
/train - Запустить обучение модели

/retrain - Переобучить модель

/generate - Сгенерировать новые прогнозы

/results - Аналитика обучения

Команды прогнозов
/predictions - Последние прогнозы

Системные команды
/logs - Информация о логах

tail -f /opt/model/logs/telegram_bot.log
