# Базовый образ для сборки
FROM python:3.11-slim-bullseye

# Установка рабочей директории
WORKDIR /app

# Установка Poetry
RUN pip install "poetry==1.5.1"

# Копируем файлы requirements и устанавливаем зависимости
COPY pyproject.toml poetry.lock /app/
RUN pip install "poetry==1.5.1"
RUN poetry config virtualenvs.create false
RUN poetry install --no-dev

# Копирование кода приложения
COPY . /app/

# Установка точки входа и команды по умолчанию
CMD ["python", "src/manage.py", "runserver", "0.0.0.0:8000"]
