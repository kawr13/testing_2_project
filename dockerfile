FROM python:3.11-slim

WORKDIR /app

# Копируем только необходимые файлы
COPY requirements.txt .

# Устанавливаем зависимости
RUN pip install --no-cache-dir -r requirements.txt

# Копируем все остальные файлы проекта
COPY . .

# Указываем переменную окружения для запуска приложения
ENV PYTHONUNBUFFERED=1

# Используем CMD для запуска приложения
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000", "--reload"]