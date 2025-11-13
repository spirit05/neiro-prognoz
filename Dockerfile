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

# Создание директорий для данных и логирования
RUN mkdir -p /app/data /app/logs /app/models

# Переменные окружения
ENV PYTHONPATH=/app
ENV ENVIRONMENT=production

# Проверяем что файлы на месте
RUN ls -la tests/ && echo "✅ Файлы tests проверены"

# Запуск тестов
CMD ["python", "-m", "pytest", "tests/", "-v", "--disable-warnings"]
