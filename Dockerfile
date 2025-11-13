FROM python:3.9-slim

WORKDIR /app

# Установка системных зависимостей
RUN apt-get update && apt-get install -y \
    gcc \
    g++ \
    && rm -rf /var/lib/apt/lists/*

# Копирование зависимостей
COPY requirements-model.txt .

# Установка Python зависимостей
RUN pip install --no-cache-dir -r requirements-model.txt

# Копирование исходного кода
COPY . .

# Создание директорий
RUN mkdir -p /app/data /app/logs /app/models

# Переменные окружения
ENV PYTHONPATH=/app
ENV ENVIRONMENT=production

# Запуск приложения
CMD ["python", "-c", "from app.main import ModelApplication; app = ModelApplication(); app.run()"]
